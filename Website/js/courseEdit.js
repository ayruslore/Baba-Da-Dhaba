function addCo(){
  console.log(document.getElementById("course_name").value);
  DATA["Courses"][toTitleCase(document.getElementById("course_name").value)]={};
  keys.push(toTitleCase(document.getElementById("course_name").value));
  console.log(keys);
  alert("Add dishes to the course to make it a valid course!");
  viewMenu();
}
