function confirmDelete(elemType) {
    message = "Are you sure you want to delete this " + elemType + "? \nDoing so may delete any associated relationships of from other tables .";
    if(confirm(message) == true) {
        document.getElementById("confirmInput").value = "True";
    }
    else { 
         document.getElementById("confirmInput").value = "False";
         return 0;
    }          
}