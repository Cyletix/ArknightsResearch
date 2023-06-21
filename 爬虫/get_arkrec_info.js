fetch(new Request('https://arkrec.com/record/query-records', {
    method: 'POST',
    // headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    headers: {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36 Edg/108.0.1462.54",
        "Referer": "https://arkrec.com/admin/all-records",
        "Cookie": "version=4.0.0; connect.sid=s%3A-iNMch95JVP7StKFhFK82hBTQ0seqGLZ.GU0y0Ib07E2tk3yFWt1Tzw%2F5DZIEC6JRIRrMbEJulks; _id=60b37d7cd54d2600045eb2ef",
        "content-type": "application/json",
        "Referer": "https://arkrec.com/admin/all-records"
    },
    body: "param1=value1&param2=value2"
})).then((resp) => { console.log(resp) })




fetch('https://arkrec.com/record/query-records')
    .then(function (response) {
        // The response is a Response instance.
        // You parse the data into a useable format using `.json()`
        return response.json();
    }).then(function (data) {
        // `data` is the parsed version of the JSON returned from the above endpoint.
        console.log(data);  // { "userId": 1, "id": 1, "title": "...", "body": "..." }
    });





fetch("https://arkrec.com/record/query-records", {
    "headers": {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Microsoft Edge\";v=\"109\", \"Chromium\";v=\"109\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    },
    "referrerPolicy": "strict-origin-when-cross-origin",
    "body": "{\"query\":{\"category\":\"精一满级\",\"admin\":1},\"skip\":1}",
    "method": "POST",
    "mode": "cors",
    "credentials": "include"
})