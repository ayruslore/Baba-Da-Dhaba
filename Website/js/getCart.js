function populate(){
  $.ajax({
    type: "GET",
    url: redisDb+"/cart/"+uid+"/show",
    success: function(data){
      function toTitleCase(str){
        return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
      }
      data=JSON.stringify(data);
      data=data.replace(/_/g, ' ');
      data=toTitleCase(data);
      data=JSON.parse(data);
      console.log(data);
      data=JSON.parse(data);
      for(var i in data){
        var temp=i;
        console.log(i);
        for(var j=0; j<keys.length; j++){
          for(var key in DATA["Courses"][keys[j]]){
            if(temp==key){
              console.log(key);
              var x=document.getElementsByName(key);
              console.log(data[i][1]);
              x[0].value=data[i][1];
              getData2();
            }
          }
        }
      }

    },
    error: function(data){
      console.log(data);
    }
  });
}
