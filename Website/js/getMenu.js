var DATA={"Courses": {}};
var uid;
var keys=[];

function getMenu(){
  function toTitleCase(str){
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
  }
  $.ajax({
    type: "GET",
    url: redisDb+"/get_user_menu"/ + uid,
    success: function(data){
      var x=JSON.parse(data);
      console.log(x);
      for(var i=0; i<x.length; i++)
        DATA["Courses"][x[i]["course"]]={};
      for(var i=0; i<x.length; i++)
        DATA["Courses"][x[i]["course"]][toTitleCase(x[i]["name"].replace(/_/g, ' '))]=[x[i]["price"], x[i]["v_n"], x[i]["stock"]];
      console.log(DATA);
      for(var key in DATA["Courses"])
        keys.push(key);

      populate();
      viewMenu();
      courses();
      courses2();
      document.getElementById("course1").click();
    },
    error: function(data){
      console.log('Nope!');
    }
  });
}

function getURL(){
  var str = window.location.href;
  uid="";
  for (var i = 0; i<=str.length; i++){
    //console.log(str.charAt(i));
    if (str.charAt(i) == "="){
      for ( var j=i+1; j<str.length; j++){
        if(str.charAt(j)=="#")
          break;
        uid = uid + str.charAt(j);
      }
      break;
    }
  }
  console.log(str);
  console.log(uid);
}
