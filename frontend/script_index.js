function validateForm() {
    var text = document.getElementById("text-input").value.trim();
    if (text === "") {
      alert("Please enter a story.");
      return false;
    }
    return true;
  }

