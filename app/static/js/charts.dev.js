/* 
* @Author: 丁以然
* @Date:   2015-01-26 18:51:27
* @Last Modified by:   丁以然
* @Last Modified time: 2015-03-25 11:35:45
*/
function PushHighstock() {
$(document).ready(function(){
    
    function replaceAll(s1,s2,s3){
        var r = new RegExp(s2.replace(/([\(\)\[\]\{\}\^\$\+\-\*\?\.\"\'\|\/\\])/g,"\\$1"),"ig");
        return s1.replace(r,s3);
    }

    var domain = '172.26.152.6:9000/show_orzdba';
    //var domain = '/show_orzdba';

    $("body div").each(function(i) {
       var type = $(this).attr("type");
       //alert(type)
       var id = $(this).attr("id");
       //alert(id)
       var cid = $(this).attr("cid");
       var user_data = $(this).attr("data");
       var image = $(this).attr("image");
       var project = $(this).attr("project");
       var opposite = $(this).attr("opposite");
       var ctitle = $(this).attr("ctitle");
       var rangetime = $(this).attr("rangetime");
       var cut = $(this).attr("cut");

       if (id && type) {

         if (!opposite) {
             opposite = "";
         }
         if (!ctitle) {
             ctitle = "";
         }
         

         if (user_data) {
             user_data = user_data.replace("}", ", ");
             user_data += "'id' : '" + id + "'}";
             console.log(user_data);
         }

         try {
             var startwith = type.indexOf('jigsaw-')
         }catch(e){
             $("#"+replaceAll(id, "|", "\\|")).html("type can not null!");
         }

         if (startwith == 0) {
             if (image == 'true' && type == 'jigsaw-chart'){
                 $.getJSON("http://"+domain+"/generate_stock_image?id="+id+"&cid="+cid+"&type="+type+"&callback=?",  function(data){
                    console.log(data);
                    $("#"+replaceAll(id, "|", "\\|")).html("<img src='http://"+domain+"/static/public/img/"+data.file+".png'/>" );
                 });
             }
             //============================================================================
             //customized project method
             else if (project){
                 $.getJSON("http://"+domain+"/stock_project?id="+id+"&cid="+cid+"&type="+type+"&project="+project+"&opposite="+opposite+"&ctitle="+ctitle+"&rangetime="+rangetime+"&cut="+cut,  function(data){
                 //$.getJSON("http://"+domain+"/stock_project?id="+id+"&cid="+cid+"&type="+type+"&project="+project+"&opposite="+opposite+"&ctitle="+ctitle+"&rangetime="+rangetime+"&cut="+cut+"&callback=?",  function(data){
                    console.log(data);
                    $("#"+replaceAll(id, "|", "\\|")).html(data.a);
                 });
             }
   
              //============================================================================
             //static data
             else if (user_data){
                 var url = "";
                 if (type == 'jigsaw-chart'){
                     url = 'http://'+domain+'/static_generate_pic';
                 }
                 else if(type == 'jigsaw-column'){
                     url = 'http://'+domain+'/static_generate_column';
                 }
                 else if(type == 'jigsaw-pie'){
                     url = 'http://'+domain+'/static_generate_pie';
                 }


                 $.getJSON(url+"?id="+id+"&type="+type+"&data="+user_data+"&callback=?",  function(data){
                    console.log(data);
                    $("#"+replaceAll(id, "|", "\\|")).html(data.a);
                 });

  /*
                 $.ajax({
                     async:false,
                     url: url,
                     type: "POST",
                     dataType: 'jsonp',
                     jsonp: 'jsoncallback',
                     data: user_data,
                     timeout: 5000,
                     beforeSend: function(){
                        //jsonp 
                     },
                     success: function (data) {
                         console.log(data);
                         $("#"+replaceAll(id, "|", "\\|")).html(data.a);
                     },
                     complete: function(XMLHttpRequest, textStatus){
                         //$.unblockUI({ fadeOut: 10 }); 
                     },
                     error: function(xhr){
                        alert(xhr);
                    }
                });
  */
             }
             //==========================================================================
             //db
             else{
                 $.getJSON("http://"+domain+"/generate_pic?id="+id+"&cid="+cid+"&type="+type+"&callback=?",  function(data){
                    console.log(data);
                    $("#"+replaceAll(id, "|", "\\|")).html(data.a);
                 });
             };
         };

        }
    });

});
}
