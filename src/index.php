<?php
define("DATA_DIR", dirname(__FILE__) . '/data');
global $wait;
$wait = FALSE;
$text = '';
$url = isset($_GET['url']) ? $_GET['url'] : '';
if ($url) {
    $text = getSubtitles($url);
}
?>

<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>字幕取り出しツール</title>
</head>

<body>

    <?php if ($url === "") : ?>
        <h1>以下に動画のURLを入力してください</h1>
        <form action="index.php" method="get">
            <input type="text" name="url" size="60" value="<?php echo htmlspecialchars($url, ENT_QUOTES); ?>">
            <input type="submit" value="取得">
        </form>
    <?php endif; ?>

    <?php if ($url) : ?>
        <h1>取り出した字幕データ</h1>
        <textarea id="subtitle" cols="60" rows="30"><?php echo htmlspecialchars($text, ENT_QUOTES); ?></textarea>

        <h3>動画のURL</h3>
        <form action="index.php" method="get">
            <input type="text" name="url" size="60" value="<?php echo htmlspecialchars($url, ENT_QUOTES); ?>">
            <input type="submit" value="再取得">
        </form>
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
function getSubtitles($url)
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
    if (file_exists($textFile)) {
        if (file_exists($lockFile)) {
            unlink($lockFile);
        }
        return file_get_contents($textFile);
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

function changeExt($file, $ext) {
    $file = preg_replace('/\.\w+$/', $ext, $file);
    return $file;
}
