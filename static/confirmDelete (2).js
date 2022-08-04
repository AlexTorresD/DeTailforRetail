function confirmDelete(elemType) {
    message = "Are you sure you want to delete this " + elemType + "? \nDoing so may delete any associated cooks relationship.";
    if(confirm(message) == true) {
        document.getElementById("confirmInput").value = "True";
    }
    else { 
         document.getElementById("confirmInput").value = "False";
         return 0;
    }          
}