var cartJSON;

function checkout(){
  document.getElementsByTagName("BODY")[0].style.display="none";
  window.alert("Close this webview/tab to proceed.");
  $.ajax({
    type: "GET",
    url: nodejsScript+"/showcart",
    data: {
      'Id': uid
    },
    success: function(data){
      console.log('Success!');
    },
    error: function(data){
      console.log('Nope!');
    }
  });
  //location.href="payment.html?userId="+uid;
  //sessionStorage.setItem('total', document.getElementById("amt").innerHTML);
}

function sender(dish, qty){
  cartJSON={};
  for(var i=0; i<dish.length; i++)
    cartJSON[dish[i].replace(/ /g, '_').toLowerCase()]=""+qty[i];
  cartJSON=JSON.stringify(cartJSON);
}

function finalSend(){
  console.log(cartJSON);
  $.ajax({
    type: "GET",
    url: redisDb+"/cart/"+uid+"/replace/"+cartJSON,
    data: "",
    success: function(data){
      console.log('Success!');
    },
    error: function(data){
      console.log('Nope!');
    }
  });
  console.log("After");
}
