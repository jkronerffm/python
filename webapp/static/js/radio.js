function editSender(id) {
    window.location.replace('/radio/sender/edit?id='+id);
}

function setActive(name) {
  const xhttp = new XMLHttpRequest();
  xhttp.onload = function() {
   };
  xhttp.open("GET", "/radio/waketime/set_active?name=" + name, true);
  xhttp.send();
  
  showFlash('(De-)Aktivierung der Weckzeit war erfolgreich')
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

function showFlash(message) {
    var popup = document.getElementById('messagePopup');
    popup.classList.toggle("show");
    popup.innerText=message;
}

function uploadFiles(fileList, dest) {
  var boundary = Math.random().toString().substr(2);
  var xmlHttpRequest = new XMLHttpRequest();
  xmlHttpRequest.open("POST", "/radio/" + dest, true);
  var dashes = "--";
  var crlf = "\r\n";
  filetype = fileList[0].type
  
  var postDataStart = dashes + boundary + crlf + "Content-Disposition: form-data;" + "name=\"file\";" + encodeURIComponent(fileList[0].name) + "\"" + crlf + "Content-Type: " + filetype + crlf + crlf;
  var postDataEnd = crlf + dashes + boundary + dashes;
  
  xmlHttpRequest.setRequestHeader("Content-Type", "multipart/related;type=application/dicom;boundary=" + boundary + ";");
  xmlHttpRequest.setRequestHeader("Accept", "application/dicom+json");
  xmlHttpRequest.send(new Blob([new Blob([postDataStart]), fileList[0], new Blob([postDataEnd])]));
}
