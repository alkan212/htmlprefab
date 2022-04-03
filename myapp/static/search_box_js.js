
function get_searchBox_items_value(searchBox_id){
    var items_array = []
    var parent = document.getElementById(searchBox_id)
    var items = parent.getElementsByClassName("search_items_value")
    for(var i = 0; i < items.length; i++){
        items_array.push(items[i])
    }

    document.getElementById("search_box_input").addEventListener("focus", function(e){
        
        var c_style = getComputedStyle(this.parentElement)
        var show = parseFloat(c_style.getPropertyValue("--show"))
        var items_height = parseInt(c_style.getPropertyValue("--items-height"))

        this.parentElement.children[1].style.maxHeight = (show*items_height).toString()+"px";
        this.parentElement.children[1].style.opacity = "1";
    })

    
    document.getElementById("search_box_input").addEventListener("focusout", function(e){
        this.parentElement.children[1].style.maxHeight = null;
        this.parentElement.children[1].style.opacity = null;
    })

    return items_array;
}



function search_box_searcher(item_array){
    document.getElementById("search_box_input").addEventListener("input", function(e){
        var value = this.value.toLowerCase()
        for(var i = 0; i < item_array.length; i++){
            if(item_array[i].innerText.includes(value)){
                item_array[i].parentElement.style.height = null;
                item_array[i].parentElement.style.opacity = null;
            }else{
                item_array[i].parentElement.style.height = "0px";
                item_array[i].parentElement.style.opacity = "0";
            }
        }
    })
}

