<?php
define("DATA_DIR", dirname(__FILE__) . '/data');
global $wait;
$wait = FALSE;
$text = '';
$url = empty($_GET['url']) ? '' : $_GET['url'];
$time = empty($_GET['time']) ? '' : $_GET['time'];
if ($url) {
    $text = getSubtitles($url, $time);
}

$urlEnc = htmlspecialchars($url, ENT_QUOTES);
$timeEnc = ($time === 'on') ? 'checked' : '';
$form = <<< EOS
    <h1>以下に動画のURLを入力してください</h1>
    <div style="border:1px solid silver; padding:1em;">
    <form action="index.php" method="get">
        URL:<br>
        <input type="text" name="url" size="60" value="$urlEnc"><br>
        <input type="checkbox" id="time" name="time" value="on" $timeEnc><label for="time">時間を表示</label><br>
        <input type="submit" value="字幕を取得">
    </form>
    </div>
EOS;

?>

<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>字幕取り出しツール</title>
</head>

<body>

    <?php
        if ($url === "") {
            echo "<h1>動画(MP4)から字幕取り出しツール</h1>";
            echo $form; 
            echo "<div style='color:red;'>(注意) このツールを使うには動画に字幕が含まれている必要があります。</div>";
        } 
    ?>

    <?php if ($url) : ?>
        <h1>取り出した字幕データ</h1>
        <textarea id="subtitle" cols="60" rows="30"><?php echo htmlspecialchars($text, ENT_QUOTES); ?></textarea>

        <h3>動画のURL</h3>
        <?php echo $form; ?>
        <hr>
        <div><a href="./index.php">新規字幕</a></div>

    <?php endif; ?>
</body>

<script>
    var wait = <?php echo $wait ? 'true' : 'false'; ?>;
    if (wait) {
        console.log('3秒後にリロードします。')
        setTimeout(() => {
            window.location.reload();
        }, 3000);
    }
</script>

</html>

<?php
function getSubtitles($url, $time)
{
    if ($url == "") {
        return "URLを指定してください。";
    }
    global $wait;
    // URLの例
    // https://d34ji3l0qn3w2t.cloudfront.net/d8ae7413-3de7-4ca6-993d-cf575ec9afc8/2/mwbv_J_202401_01_r240P.mp4
    // https://www.jw.org/ja/%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA%E3%83%BC/%E3%83%93%E3%83%87%E3%82%AA/#ja/mediaitems/VODOrgBloodlessMedicine/pub-mwbv_202401_1_VIDEO
    $baseURL = preg_replace('/\?\w+$/', '', $url);
    $baseURL = basename($baseURL);
    $textFile = DATA_DIR . '/' . changeExt($baseURL, '.txt');
    $lockFile = DATA_DIR . '/' . $baseURL . '.lock';
    $logFile = DATA_DIR . '/log.txt';
    $mp4File = DATA_DIR . '/' . $baseURL;
    if (file_exists($textFile)) {
        // clear cache
        if (file_exists($lockFile)) {
            @unlink($lockFile);
            if (file_exists($mp4File)) {
                @unlink($mp4File);
            }
        }
        $text = file_get_contents($textFile);
        if ($time !== 'on') {
            $result = "";
            $lines = explode("\n", $text);
            foreach ($lines as $line) {
                $line = trim($line);
                $line = preg_replace('/^\d+\:\d+:\d+\>/', '', $line);
                $line = trim($line);
                $result .= $line . "\n";
            }
            $text = $result;
        }
        return $text;
    }
    if (preg_match('/\.mp4$/', $baseURL)) {
        file_put_contents($lockFile, 'lock');
        $path = __DIR__ . '/mp4topdf.py';
        $wait = TRUE;
        $cmd = "/usr/bin/env python3 \"{$path}\" \"$url\" > \"$logFile\" 2>&1 &";
        @exec($cmd);
        return "現在取得しています。しばらくお待ちください。";
    } else {
        return "残念。直接MP4ファイルのURLを指定してください。";
    }
}

function changeExt($file, $ext)
{
    $file = preg_replace('/\.\w+$/', $ext, $file);
    return $file;
}
