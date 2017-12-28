var DATA={"Courses": {}};
var keys=[]

$.ajax({
  type: "GET",
  url: redisDb+"/get_menu",
  success: function(data){
    var x=JSON.parse(data);
    //console.log(x);
    for(var i=0; i<x.length; i++)
      DATA["Courses"][x[i]["course"]]={};
    for(var i=0; i<x.length; i++)
      DATA["Courses"][x[i]["course"]][toTitleCase(x[i]["name"].replace(/_/g, ' '))]=[x[i]["price"], x[i]["v_n"], x[i]["stock"]];
    console.log(DATA);
    for (var key in DATA["Courses"])
      keys.push(key);

    viewMenu();
  },
  error: function(data){
    console.log(data);
  }
});


function toTitleCase(str){
  return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

function openCourse2(event, courseName) {
    // Declare all variables
    var i, tabcontent, tablinks;
    console.log();
    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent2");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        console.log(tablinks[i]);
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(courseName).style.display = "block";
    //event.currentTarget.className += " active";
}

function viewMenu(){
  document.getElementById("display").innerHTML="";
  //tags for courses
  var d1=document.createElement("DIV");
  d1.className="widget widget-tags";
  for(var i in DATA["Courses"]){
    var a1=document.createElement("A");
    a1.href="#";
    a1.innerHTML=i;
    a1.onclick=function(){
      openCourse2(event, this.innerHTML);
    }
    d1.appendChild(a1);
  }
  document.getElementById("display").appendChild(d1);
  //content for each tab
  for(var i in DATA["Courses"]){
    //console.log(i);
    var cou=document.createElement("DIV");
    cou.className="tabcontent2";
    cou.id=i;
    //document.getElementById("display").innerHTML+="<br><br><strong>"+i+"<strong><br>";
    for(var j in DATA["Courses"][i]){
      //console.log(j);
      var dis=document.createElement("A");
      dis.id=j;
      dis.onclick=function(){
        //console.log(this.parentNode.id, this.id);
        changeAvail(this.parentNode.id, this.id);
      }
      dis.innerHTML=j+" - Rs. "+ DATA["Courses"][i][j][0] +" - "+DATA["Courses"][i][j][1];
      if(DATA["Courses"][i][j][2]=="In")
        //document.getElementById("display").innerHTML+='<a href="#" class="btn btn-pill btn-primary waves-effect waves-light" onclick="changeAvail("'+key+'")">'+key+" - Rs. "+DATA["Courses"][keys[i]][key][0]+" - "+DATA["Courses"][keys[i]][key][1]+'</a>';
        dis.className="btn btn-pill btn-primary waves-effect waves-light";
      else
        //document.getElementById("display").innerHTML+='<a href="#" class="btn btn-pill btn-danger waves-effect waves-light" onclick="changeAvail("'+key+'")">Update Menu</a>';
        dis.className="btn btn-pill btn-danger waves-effect waves-light";
      cou.appendChild(dis);
    }
    document.getElementById("display").appendChild(cou);
  }
  addD("addDish_");
  addD("removeDish_");
}

function changeAvail(c, d){
  if(DATA["Courses"][c][d][2]=="Out") DATA["Courses"][c][d][2]="In";
  else DATA["Courses"][c][d][2]="Out";
  console.log(d.replace(/ /g, '_').toLowerCase());
  $.ajax({
    type: "GET",
    url: redisDb+"/outofstock/"+d.replace(/ /g, '_').toLowerCase(),
    success: function(data){
      viewMenu();
    },
    error: function(data){
      console.log(data);
    }
  });
  viewMenu();
}

function addOrder(orderId, order, loc, status){
  if(status=="rejected") return;
  //<div class="panel">
  var d1=document.createElement("DIV");
  d1.className="panel";
  d1.id="o"+orderId;
  //<div class="panel-heading">
  var d2=document.createElement("DIV");
  d2.className="panel-heading";
  //<a class="panel-title collapsed" data-toggle="collapse" data-parent="#accordion" href="#orderId" aria-expanded="false">
  var a1=document.createElement("A");
  a1.className="panel-title collapsed";
  a1.setAttribute("data-toggle", "collapse");
  a1.setAttribute("data-parent", "#accordion"+loc);
  a1.href="#"+orderId;
  a1.setAttribute("aria-expanded", "false");
  d2.innerHTML+="Order Number #"+orderId;
  var w1=document.createElement("WQ");
  w1.href="#";
  w1.id=orderId+"status";
  w1.className="btn btn-pill btn-sm btn-primary waves-effect waves-light";
  if(status=="pending"){
    w1.innerHTML="Accept";
    w1.onclick=function(){
      changeStatus('Accepted', orderId);
    }
  }
  else if(status=="order_accepted"){
    w1.innerHTML="Accepted";
    w1.onclick=function(){
      changeStatus('In Kitchen', orderId);
    }
  }
  else if(status=="in_kitchen"){
    w1.innerHTML="In Kitchen";
    w1.onclick=function(){
      changeStatus('Out For Delivery', orderId);
    }
  }
  else if(status=="out_for_delivery"){
    w1.innerHTML="Out For Delivery";
    w1.onclick=function(){
      changeStatus('Delivered', orderId);
    }
  }
  a1.appendChild(w1);
  var w2=document.createElement("WQ");
  w2.href="#";
  w2.id=orderId+"statusReject";
  w2.className="btn btn-pill btn-sm btn-danger waves-effect waves-light";
  w2.innerHTML="Reject";
  w2.onclick=function(){
    changeStatus('Rejected', orderId);
  }
  if(status=="pending") a1.appendChild(w2);
  d2.appendChild(a1);
  d1.appendChild(d2);
  var d3=document.createElement("DIV");
  d3.id=orderId;
  d3.className="panel-collapse collapse";
  d3.setAttribute("role", "tabpanel");
  d3.setAttribute("aria-expanded", "false");
  d3.style="height: 0px;"
  var d4=document.createElement("DIV");
  d4.innerHTML=order+"<br>";
  d4.className="panel-body text-gray";
  /*
  var a2=document.createElement("A");
  a2.href="#";
  a2.id=orderId+"kitchen";
  a2.className="btn btn-ghost btn-pill btn-sm btn-danger waves-effect waves-light";
  a2.onclick=function(){
    changeStatus('In Kitchen', orderId);
  }
  a2.innerHTML="In Kitchen";
  var a3=document.createElement("A");
  a3.href="#";
  a3.id=orderId+"delivery";
  a3.className="btn btn-ghost btn-pill btn-sm btn-warning waves-effect waves-light";
  a3.onclick=function(){
    changeStatus('Out For Delivery', orderId);
  }
  a3.innerHTML="Out For Delivery";
  var a4=document.createElement("A");
  a4.href="#";
  a4.id=orderId+"success";
  a4.className="btn btn-ghost btn-pill btn-sm btn-success waves-effect waves-light";
  a4.onclick=function(){
    changeStatus('Delivered', orderId);
  }
  a4.innerHTML="Delivered";
  //if(status=="accepted" || status=="pending") d4.appendChild(a2);
  //if(status=="pending" || status=="in_kitchen" || status=="accepted") d4.appendChild(a3);
  //if(status=="pending" || status=="out_for_delivery" || status=="in_kitchen" || status=="accepted") d4.appendChild(a4);
  */
  d3.appendChild(d4);
  d1.appendChild(d3);
  document.getElementById("accordion"+loc).appendChild(d1);
}

function changeStatus(obj, orderId){
  if(obj=="Accepted"){
    $.ajax({
      type: "GET",
      url: redisDb+"/cart/"+orderId+"/accept",
      success: function(data){
        console.log('Success!');
      },
      error: function(data){
        console.log('Nope!');
      }
    });
  }
  else if(obj=="In Kitchen"){
    $.ajax({
      url: redisDb+"/cart/"+orderId+"/in_kitchen",
      success: function(data){
        console.log('Success!');
      },
      error: function(data){
        console.log('Nope!');
      }
    });
  }
  else if(obj=="Out For Delivery"){
    var delGuy=prompt("Please enter delivery boy's phone number", "");
    if (delGuy!=null){
      console.log(delGuy);
      $.ajax({
        type: "GET",
        url: redisDb+"/cart/"+orderId+"/out_for_delivery/"+delGuy,
        success: function(data){
          console.log('Success!');
        },
        error: function(data){
          console.log('Nope!');
        }
      });
    }
  }
  else if(obj=="Delivered"){
    $.ajax({
      type: "GET",
      url: redisDb+"/cart/"+orderId+"/delivered",
      success: function(data){
        console.log('Success!');
      },
      error: function(data){
        console.log('Nope!');
      }
    });
  }
  document.getElementById(orderId+"status").innerHTML=obj;
  if(obj=="Rejected"){
    document.getElementById("o"+orderId).remove();
    $.ajax({
      type: "GET",
      url: redisDb+"/cart/"+orderId+"/reject",
      data: "",
      success: function(data){
        console.log('Success!');
      },
      error: function(data){
        console.log('Nope!');
      }
    });
  }
}

/*
[
{
  "id": "1446107422137541",
  "cart": {"tawa_roti": "6"}
},
{
  "id": "1446107422137541",
  "cart": {}
},
{
  "id": "1601355239935835",
  "cart": {"chicken_makhanwala": "3", "wheat_tawa_roti": "2"}
},
{
  "id": "1601355239935835",
  "cart": {}
}
]
*/

function ordr(data, loc){
  function toTitleCase(str){
    return str.replace(/\w\S*/g, function(txt){
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
  }
  for(var item in data){
    console.log(data[item]["id"], JSON.stringify(data[item]["cart"]));
    if(JSON.stringify(data[item]["cart"])!={}){
      var temp=data[item]["cart"];
      var x="";
      for(var i in temp)
        x+=toTitleCase(String(i.replace(/_/g, ' ')))+": "+String(temp[i])+"<br>";
      addOrder((data[item]["id"]), "<li>Name: "+(data[item]["data"]["name"])+"</li><li>Phone Number: "+(data[item]["data"]["number"])+"</li><li>Address: "+(data[item]["data"]["address"])+"</li><li>"+x+"</li>", loc, data[item]["status"]);
    }
  }
}

function saffron(){
  document.getElementById("accordionis_1").innerHTML="";
  $.ajax({
    url: redisDb+'/read_orders',
    success: function(data) {
      data=JSON.parse(data);
      console.log(data);
      ordr(data, "is_1");
    },
    error: function(data){
      console.log(data);
    }
  });
}

function discount(){
  var disc=document.getElementById('discount_per').value;
  if(disc<0 & disc>80){
    alert("Discount % not allowed!");
    return;
  }
  $.ajax({
    url: redisDb+'/discount/'+disc,
    success: function(data) {
      console.log(data);
      alert("Discount added! Enter 0 to remove the discount!");
    },
    error: function(data){
      console.log(data);
    }
  });
}
