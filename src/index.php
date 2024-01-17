<?php
define("DATA_DIR", dirname(__FILE__) . '/data');
$text = '';
$url = isset($_POST['url']) ? $_POST['url'] : '';
if ($url) {
    $text = getSubtitles($url);
}
?>
<html>
    <head>
        <meta charset="UTF-8">
        <title>字幕取り出しツール</title>
    </head>
    <body>
        <h1>以下に動画のURLを入力してください</h1>
        <form action="index.php" method="post">
            <input type="text" name="url" size="100">
            <input type="submit" value="取得">
        </form>
        <h1>取り出した字幕データ</h1>
        <textarea id="subtitle" cols="100" rows="30"><?php echo htmlspecialchars($text, ENT_QUOTES); ?></textarea>
    </body>
</html>
<?php
function getSubtitles($url) {
    // URLの例
    // https://d34ji3l0qn3w2t.cloudfront.net/d8ae7413-3de7-4ca6-993d-cf575ec9afc8/2/mwbv_J_202401_01_r240P.mp4
    // https://www.jw.org/ja/%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA%E3%83%BC/%E3%83%93%E3%83%87%E3%82%AA/#ja/mediaitems/VODOrgBloodlessMedicine/pub-mwbv_202401_1_VIDEO
    $baseURL = preg_replace('/\?\w+/', '', $url);
    $textFile = DATA_DIR.'/'.preg_replace('/.(mp4|avi|wmv)$/', '.txt', $baseURL);
    if (file_exists($textFile)) {
        return file_get_contents($textFile);
    }
    if (preg_match('/\.mp4$/', $baseURL)) {
        $text = getSubtitlesFromMp4($baseURL);
    } else {
        $text = getSubtitlesFromJW($baseURL);
    }
    $text = '';
    $video_id = getVideoId($url);
    if ($video_id) {
        $text = getSubtitlesFromVideoId($video_id);
    }
    return $text;
}