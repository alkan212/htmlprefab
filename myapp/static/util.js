var URL = "http://www.htmlprefab.com";

String.prototype.format = function() {
    a = this;
    for (k in arguments) {
    a = a.replace("{" + k + "}", arguments[k])
    }
    return a
}
function copy_text(text){
    navigator.clipboard.writeText(text);
}

function noneFunction(){
    
}

function send_post(path, data=undefined, func=noneFunction){

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", path, true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            /*var msg = JSON.parse(this.responseText); */
            
            func(this.responseText);
        };
    }

    if(data !== undefined){
        let t = ""
        for(let obj of Object.keys(data)){
            t = t + "&" + obj + "=" + data[obj];
        }
    
        xmlhttp.send(t);

    }else{
        xmlhttp.send();
    }

}


function onOver(element, targetElement ,newStyle){
    element.addEventListener("mouseover", function(e){setNewStyle(e, targetElement)})
    element.addEventListener("mouseout", function(e){resetNewStyle(e, targetElement)})

    var properties = Object.keys(newStyle)
    function setNewStyle(e, targetElement){
        for(var i = 0; i < properties.length; i++){
            targetElement.style.setProperty(properties[i], newStyle[properties[i]])
        }
    }

    function resetNewStyle(e, targetElement){
        for(var i = 0; i < properties.length; i++){
            targetElement.style.setProperty(properties[i], null)
        }
    }
}





function send_get(path, data=undefined, func=noneFunction){

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET", path, true);
    xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    
    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            /*var msg = JSON.parse(this.responseText); */
            
            func(this.responseText);
        };
    }

    if(data !== undefined){
        let t = ""
        for(let obj of Object.keys(data)){
            t = t + "&" + obj + "=" + data[obj];
        }
    
        xmlhttp.send(t);

    }else{
        xmlhttp.send();
    }

}
