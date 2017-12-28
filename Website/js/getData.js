var x=[], y=[];
function getData2(){
  document.getElementById("display").innerHTML="";
  function imageName(nameD){
    return nameD.replace(/ /g, '-');
  }
  var course=[];
  var dish=[];
  var qty=[]

  var total=0, items=0;
  for(var i=0; i<keys.length; i++){
    for (var key in DATA["Courses"][keys[i]]){
      var vl=Number(document.getElementsByName(key)[0].value);
      if(vl!=0){
        course.push(keys[i]);
        dish.push(key);
        qty.push(vl);
      }
    }
  }

  for(var i=0; i<dish.length; i++){
    //<div class="item">
    var d1=document.createElement("DIV");
    d1.className="item";
    //<a href="shop-single.html" class="item-thumb">
    var a1=document.createElement("A");
    a1.className="item-thumb";
    /*
    <img src="img/cart/item02.jpg" alt="Item">
    var im1=document.createElement("IMG");
    im1.src="img/db/"+imageName(dish[i])+".jpg";
    a1.appendChild(im1);
    d1.appendChild(a1);
    */
    //<div class="item-details">
    var d2=document.createElement("DIV");
    d2.className="item-details filters-bar";
    //<h3 class="item-title">
    var hd1=document.createElement("H3");
    hd1.className="item-title column";
    hd1.innerHTML=dish[i]+" (&#8377;"+DATA["Courses"][course[i]][dish[i]][0]*qty[i]+")";
    if(DATA["Courses"][course[i]][dish[i]][1]=="veg")
      hd1.style.color="green";
    else
      hd1.style.color="red";
    d2.appendChild(hd1);
    /*
    //<h4 class="item-price">
    var hd2=document.createElement("H4");
    hd2.className="item-price column";
    hd2.innerHTML="&#8377;"+DATA["Courses"][course[i]][dish[i]][0]*qty[i];
    d2.appendChild(hd2);
    */
    total+=Number(DATA["Courses"][course[i]][dish[i]][0]*qty[i]);
    //<div class="count-input">
    var d3=document.createElement("DIV");
    d3.className="count-input column";
    //<a class="incr-btn" data-action="decrease" href="#">–</a>
    var a2=document.createElement("A");
    a2.className="incr-btn";
    a2.setAttribute("data-action", "decrease");
    a2.href='#';
    a2.innerHTML='-';
    d3.appendChild(a2);
    //<input class="quantity" name="c1_10" type="text" value="0">
    var i1=document.createElement("INPUT");
    i1.setAttribute("type", "text");
    i1.className="quantity";
    i1.value=Number(document.getElementsByName(dish[i])[0].value);
    items+=Number(document.getElementsByName(dish[i])[0].value);
    i1.name=dish[i];
    d3.appendChild(i1);
    //<a class="incr-btn" data-action="increase" href="#">+</a>
    var a3=document.createElement("A");
    a3.className="incr-btn";
    a3.setAttribute("data-action", "increase");
    a3.href='#';
    a3.innerHTML='+';
    d3.appendChild(a3);
    d2.appendChild(d3);
    d1.appendChild(d2);
    //<a href="#" class="item-remove" data-toggle="tooltip" data-placement="top" title="Remove">
    var a4=document.createElement("A");
    a4.className="item-remove";
    a4.setAttribute("data-toggle", "tooltip");
    a4.setAttribute("data-placement", "top");
    a4.setAttribute("title", "Remove");
    a4.onclick=function(){
      removeItem(this);
    }
    //<i class="material-icons remove_shopping_cart"></i>
    var i2=document.createElement("I");
    i2.className="material-icons remove_shopping_cart";
    a4.appendChild(i2);
    //d1.appendChild(a4);
    document.getElementById("display").appendChild(d1);
  }
  document.getElementById("amt").innerHTML="&#8377;"+total;
  document.getElementById("item_qty").innerHTML=items;
  document.getElementById("item_qty2").innerHTML="Currently "+items+" items are in your basket.";
  x=dish, y=qty;
}

function removeItem(obj){
  console.log(obj.parentNode.childNodes[1].childNodes[2].childNodes[1]);
  var v=(obj.parentNode.childNodes[1].childNodes[2].childNodes[1].name);
  syncValues(v, 0);
  getData2();
}

function syncValues(v1, val){
  /*
  var temp=document.getElementsByName(v1);
  for(var i=0; i<temp.length; i++)
    temp[i].setAttribute("value", v1);
  */
  document.getElementsByName(v1)[0].value=val;
  document.getElementsByName(v1)[1].value=val;
  if(document.getElementsByName(v1)[2]!=null)
    document.getElementsByName(v1)[2].value=val;
  getData2();
  sender(x, y);
  finalSend();
}
