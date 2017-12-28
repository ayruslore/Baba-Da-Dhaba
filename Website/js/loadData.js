//keys[i]=course
//key=dish name
//DATA["Courses"][keys[i]][key][0]=Veg/Non Veg
//DATA["Courses"][keys[i]][key][1]=price

function courses(){
  for(var i=0; i<keys.length; i++){
    var l1=document.createElement("LI");
    var a1=document.createElement("A");
    a1.innerHTML=keys[i];
    a1.href="#";
    a1.id="course"+i;
    a1.onclick=function(){
      openCourse(event, this.id+"_tab");
    }
    l1.appendChild(a1);
    document.getElementById('courseDisplay').appendChild(l1);
  }
}

function courses2(){
  for(var i=0; i<keys.length; i++){
    var a1=document.createElement("A");
    a1.innerHTML=keys[i];
    a1.href="#";
    a1.id="course"+i+"_";
    a1.onclick=function(){
      openCourse(event, this.id+"tab");
    }
    document.getElementById('courseDisplay2').appendChild(a1);
  }
}

function viewMenu(){
  function imageName(nameD){
    return nameD.replace(/ /g, '-');
  }
  document.getElementById("dishDisplay").innerHTML="";
  for(var i=0; i<keys.length; i++){
    var tabCourse=document.createElement("DIV");
    tabCourse.id="course"+i+"_tab";
    tabCourse.className="tabcontent";
    var hed=document.createElement("H3");
    hed.className="toolbar-title";
    hed.innerHTML=keys[i];
    tabCourse.appendChild(hed);
    //keys[i]=course
    var j=0;
    //<div class="row">
    var d7=document.createElement("DIV");
    d7.className="shopping-cart"
    for(var key in DATA["Courses"][keys[i]]){
      //<div class="item">
      var d1=document.createElement("DIV");
      d1.className="item";
      //<a href="shop-single.html" class="item-thumb">
      var a1=document.createElement("A");
      a1.className="item-thumb";
      /*
      <img src="img/cart/item02.jpg" alt="Item">
      var im1=document.createElement("IMG");
      im1.src="img/db/"+imageName(key)+".jpg";
      a1.appendChild(im1);
      d1.appendChild(a1);
      */
      //<div class="item-details">
      var d2=document.createElement("DIV");
      d2.className="item-details filters-bar";
      //<h3 class="item-title">
      var hd1=document.createElement("H3");
      hd1.className="item-title column";
      hd1.innerHTML=key+" (&#8377;"+DATA["Courses"][keys[i]][key][0]+")";
      if(DATA["Courses"][keys[i]][key][2]=="Out") hd1.innerHTML+="  ---  OUT OF STOCK";
      if(DATA["Courses"][keys[i]][key][1]=="veg")
        hd1.style.color="green";
      else
        hd1.style.color="red";
      d2.appendChild(hd1);
      /*
      //<h4 class="item-price">
      var hd2=document.createElement("H4");
      hd2.className="item-price column";
      hd2.innerHTML="&#8377;"+DATA["Courses"][keys[i]][key][0];
      d2.appendChild(hd2);
      */
      //<div class="count-input">
      if(DATA["Courses"][keys[i]][key][2]=="In"){
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
        i1.value=0;
        i1.name=key;
        d3.appendChild(i1);
        //<a class="incr-btn" data-action="increase" href="#">+</a>
        var a3=document.createElement("A");
        a3.className="incr-btn";
        a3.setAttribute("data-action", "increase");
        a3.href='#';
        a3.innerHTML='+';
        d3.appendChild(a3);
        d2.appendChild(d3);
      }
      d1.appendChild(d2);
      /*
      //<div class="count-input">
      var d1=document.createElement("DIV");
      d1.className="count-input";
      //<a class="incr-btn" data-action="decrease" href="#">–</a>
      var a1=document.createElement("A");
      a1.className="incr-btn";
      a1.setAttribute("data-action", "decrease");
      a1.href='#';
      a1.innerHTML='-';
      d1.appendChild(a1);
      //<input class="quantity" name="c1_10" type="text" value="0">
      var i1=document.createElement("INPUT");
      i1.setAttribute("type", "text");
      i1.className="quantity";
      i1.value="0";
      i1.name=key;
      d1.appendChild(i1);
      //<a class="incr-btn" data-action="increase" href="#">+</a>
      var a2=document.createElement("A");
      a2.className="incr-btn";
      a2.setAttribute("data-action", "increase");
      a2.href='#';
      a2.innerHTML='+';
      d1.appendChild(a2);
      //<div class="shop-item-tools">
      var d2=document.createElement("DIV");
      d2.className="shop-item-tools"
      d2.appendChild(d1);
      //<div class="shop-item-details">
      var d3=document.createElement("DIV");
      d3.className="shop-item-details";
      //<h3 class="shop-item-title">Chicken Makhanwala</h3>
      var hd1=document.createElement("H3");
      hd1.className="shop-item-title";
      hd1.innerHTML=key;
      d3.appendChild(hd1);
      //<span class="shop-item-price">&#8377;250</span>
      var s1=document.createElement("SPAN");
      s1.className="shop-item-price";
      s1.innerHTML="&#8377;"+DATA["Courses"][keys[i]][key][0];
      d3.appendChild(s1);
      //<div class="shop-thumbnail">
      var d4=document.createElement("DIV");
      d4.className="shop-thumbnail";
      if(DATA["Courses"][keys[i]][key][1]=="Non Veg"){
        var s2=document.createElement("SPAN");
        s2.className="shop-label text-danger"
        s2.innerHTML="Non Veg"
        d4.appendChild(s2);
      }
      //<img src="img/menu/Riveting-Desserts/Chocolate-Cake.jpg" alt="Shop item">
      var im1=document.createElement("IMG");
      im1.src="img/db/"+imageName(key)+".jpg";
      im1.alt="Image Not Available - Scroll over the image to add to your basket.";
      d4.appendChild(im1);
      d4.appendChild(d2);
      //<div class="shop-item">
      var d5=document.createElement("DIV");
      d5.className="shop-item";
      d5.appendChild(d4);
      d5.appendChild(d3);
      //<div class="col-lg-3 col-md-4 col-sm-6">
      var d6=document.createElement("DIV");
      d6.className="col-lg-3 col-md-4 col-sm-6";
      if((j%4)!=0){
        d6.appendChild(d5);
        d7.appendChild(d6);
        console.log("IF "+j);
      }
      else{
        d7=document.createElement("DIV");
        d7.className="row"
        d6.appendChild(d5);
        d7.appendChild(d6);
        console.log("ELSE "+j);
      }
      */
      d7.appendChild(d1);
      tabCourse.appendChild(d7);
      //key=dish name
      //DATA["Courses"][keys[i]][key][0]=Veg/Non Veg
      //DATA["Courses"][keys[i]][key][1]=price
    }
    document.getElementById("dishDisplay").appendChild(tabCourse);
  }
  openCourse(event, 'course1_tab');
}
