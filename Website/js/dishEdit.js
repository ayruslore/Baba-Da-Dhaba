  function addD(id_){
    document.getElementById(id_).innerHTML="SELECT COURSE<br>";
    for(var i=0; i<keys.length; i++){
      var i1=document.createElement("INPUT");
      i1.setAttribute("type", "radio");
      if(id_=="addDish_"){
        i1.id=keys[i]+"_add";
        i1.name="addDish_";
      }
      else if(id_=="removeDish_"){
        i1.id=keys[i]+"_remove";
        i1.name="removeDish_";
      }
    i1.value=keys[i];
    document.getElementById(id_).appendChild(i1);
    document.getElementById(id_).innerHTML+=keys[i]+"<br>";
  }
}

function addDi(){
  function imageName(nameD){
    return nameD.replace(/ /g, '_');
  }
  var vg;
  if(document.getElementById('Veg').checked)
    vg=document.getElementById('Veg').value;
  else vg=document.getElementById('Non Veg').value;
  var dish_name=document.getElementById('dish_name').value;
  var dish_price=document.getElementById('dish_price').value;
  var dish_ing, dish_c;
  for(var i=1; i<=6; i++){
    if(document.getElementById("ing"+i).checked){
      dish_ing=document.getElementById("ing"+i).value;
      break;
    }
  }
  for(var i=0; i<keys.length; i++){
    if(document.getElementById(keys[i]+"_add").checked){
      dish_c=document.getElementById(keys[i]+"_add").value;
      break;
    }
  }
  var dishDet={
    "v_n": vg,
    "name": imageName(dish_name.toLowerCase()),
    "price": dish_price,
    "link": "http:__ec2-35-154-42-243.ap-south-1.compute.amazonaws.com_img_hero-slider_01.jpg",
    "base_ing": dish_ing,
    "course": dish_c,
    "stock": "In"
  };
  dishDet=JSON.stringify(dishDet);

  if(dish_name.length!=0 & dish_price.length!=0 & dish_c!=null & vg!=null){
    console.log(dishDet);
    $.ajax({
      type: "GET",
      url: redisDb+"/add_dish/["+dishDet+"]",
      success: function(data){
        console.log(data);
      },
      error: function(data){
        console.log('Nope!');
      }
    });
    DATA["Courses"][dish_c][toTitleCase(dish_name)]=[dish_price, vg, "In"];
    //console.log(document.getElementById("imageFile").files[0].name);
    alert("Dish added!");
    openCourse(event, 'menuView');
    viewMenu();
  }
  else
    alert("Please fill in all the fields!");
}

function removeDi(){
  document.getElementById('removeDish_2').innerHTML="<br>";
  var course;
  for(var i=0; i<keys.length; i++){
    if (document.getElementById(keys[i]+"_remove").checked){
      course=document.getElementById(keys[i]+"_remove").value;
      break;
    }
  }
  var keys2=[];
  for (var key in DATA["Courses"][course])
    keys2.push(key);
  for(var i=0; i<keys2.length; i++){
    var in1=document.createElement("INPUT");
    in1.setAttribute("type", "radio");
    in1.id=keys2[i]+"_rem";
    in1.name="dish_rem";
    in1.value=keys2[i];
    document.getElementById("removeDish_2").appendChild(in1);
    document.getElementById('removeDish_2').innerHTML+=keys2[i]+"<br>";
  }
  var ab=document.createElement("A");
  ab.className="btn btn-ghost btn-pill btn-danger waves-effect waves-light";
  ab.innerHTML="Remove Dish!";
  ab.onclick=function(){
    remoD(keys2, course);
  }
  document.getElementById('removeDish_2').appendChild(ab);
}

function remoD(keys2, course){
  var rate_value;
  for(var i=0; i<keys2.length; i++)
    if (document.getElementById(keys2[i]+"_rem").checked)
      //console.log(document.getElementById(keys2[i]).value);
      rate_value = document.getElementById(keys2[i]+"_rem").value;
  delete DATA["Courses"][course][rate_value];
  console.log(DATA["Courses"][course]);
  //document.getElementById("courseDishes").innerHTML="";
  document.getElementById("removeDish123").click();
  var xyz=[rate_value];
  xyz=JSON.stringify(xyz);
  $.ajax({
    type: "GET",
    url: redisDb+"/delete_dish/"+xyz.replace(/ /g, '_').toLowerCase(),
    success: function(data){
      alert(rate_value+" Removed!");
      console.log(data);
    },
    error: function(data){
      console.log('Nope!');
    }
  });
}
