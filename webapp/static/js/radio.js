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

function repaintBackgroundList(fileList) {
  console.log(fileList);
  var backgroundList = document.getElementById("background")
  backgroundList.options.length = 0;
  for(var file in fileList) {
    filename = fileList[file];
    console.log("add " + filename + " to select")
    var opt = document.createElement("option");
    opt.text = filename;
    opt.value = filename;
    backgroundList.add(opt, null)
  }
  backgroundList.addEventListener("change", changeBgPic);
}
function saveBackgroundFile() {
  var imageFile = document.getElementById("imageFile");
  var fileList = imageFile.files;
  const formData = new FormData();
  formData.append("file", fileList[0]);
  const requestOptions = {
    headers: {
      "Content-Type": fileList[0].contentType,
    },
    mode: "no-cors",
    method: "POST",
    files: fileList,
    body: formData,
  };
  fetch("/radio/background/save", requestOptions)
  .then(r => r.json().then(data => ({status: r.status, body: data})))
  .then(obj => repaintBackgroundList(obj.body.background));

  return false;
}

function setImage(imageData) {
  var img = document.getElementById("backgroundImage");
  img.src = imageData;
}

function changeBgPic(callback) {
  var background = document.getElementById("background");
  const xhr = new XMLHttpRequest();
  xhr.open("GET", "/radio/background/get?image=" + background.value, true);
  xhr.onreadystatechange = () => {
    if (xhr.readyState === 4) {
      callback(JSON.parse(xhr.response).b64Image);
    }
  };
  xhr.send();
  backgroundList.addEventListener("change", changeBgPic);
}

function onClickPlaylist(checkboxId, inputId, playListId) {
  var checkBox = document.getElementById(checkboxId);
  var input = document.getElementById(inputId);
  var playLists = document.getElementById(playListId);
  var isPlaylist = checkBox.checked
  input.style.display = (isPlaylist ? 'none': 'initial');
  playLists.style.display = (isPlaylist ? 'initial' : 'none');
}    
    
