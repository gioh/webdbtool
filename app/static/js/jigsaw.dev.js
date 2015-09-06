function PushEchart() {
$(document).ready(function() {
    function replaceAll(s1, s2, s3) {
        var r = new RegExp(s2.replace(/([\(\)\[\]\{\}\^\$\+\-\*\?\.\"\'\|\/\\])/g, "\\$1"), "ig");
        return s1.replace(r, s3);
    }
    var domain = "172.26.152.6:9000/show_orzdba";

    $("body div").each(function(i) {
        var id = $(this).attr("id");
        var type = $(this).attr("type");
        var data = $(this).attr("data");

        var height = $(this).attr("height");
        if (!height) {
            height = '500px';
        }

        var width = $(this).attr("width");

        if (id && type) {
            // static data
            //if (data) {
                if (type == 'line' || type == 'column') {
                    url = '/line';
                } else if (type == 'pie') {
                    url = '/pie';
                } else if (type == 'map') {
                    url = '/map';
                } else if (type == 'map_pie') {
                    url = '/map';
                }
                //$.getJSON("http://" + domain + url + "?id=" + id + "&type=" + type + "&data=" + data + "&callback=?",
                $.getJSON("http://" + domain + url + "?id=" + id + "&type=" + type + "&data=" + data ,
                //$.getJSON("http://" + domain + url + "?id=" + id + "&type=" + type + "&data=" + data + "&callback=?",
                function(data) {
                    console.log(data.js);
                    //alert('haha');
                    //alert(data.js);

                    //data = data.replace('<script>','');
                    //data = data.replace('</script>','');
                    //$('#main').html(data);
                    //console.log(data.js);
                    //alert(data.js)
                    $("#" + replaceAll(id, "|", "\\|")).css("height", height);
                    $("#" + replaceAll(id, "|", "\\|")).css("width", width);
                    $("#" + replaceAll(id, "|", "\\|")).html(data.js);
                });
            //}
        }
    });
});
}