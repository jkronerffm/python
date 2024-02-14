function editSender(id) {
    window.location.replace('/radio/sender/edit?id='+id);
}

function setActive(name) {
  const xhttp = new XMLHttpRequest();
  xhttp.onload = function() {
   };
  xhttp.open("GET", "/radio/waketime/set_active?name=" + name, true);
  xhttp.send();
}

function editJob(name) {
  window.location.replace("/radio/waketime/edit?name="+name);
}

function switchRuntime(dateOrCron) {
  var div1 = document.getElementById('runtime_once');
  var div2 = document.getElementById('runtime_repeatedly');
  if (dateOrCron.checked) {
    div1.style.display="block";
    div2.style.display="none";
  } else {
    div1.style.display="none";
    div2.style.display="block";
  }
}

function doClone(element) {
    var name = document.getElementById("name").value
    url = "/radio/waketime/clone?name="+name;
    window.location.replace(url);
}

