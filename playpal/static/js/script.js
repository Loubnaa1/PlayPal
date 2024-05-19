//Grabs elements
const selectElement = selector => {
  const element = document.querySelector(selector)
  if (element) return element;
  throw new Error(`Sorry, that wasn't right, there is no \
    element by the name "${selector}", Please check your spelling and try again!`);
};


// Notification Js Display
function showNotifications() {
  const container = selectElement('#notification-container');

  if (container.classList.contains('d-none')) {
    container.classList.remove('d-none')
  } else {
    container.classList.add('d-none');
  }

}

// Django get cookies function
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function removeNotification(removeNotificationURL, redirectURL) {
  // A function that deletes notification
  // args:
  //      removeNotification -> the notification url
  //      reidirectURL -> redirects after removing notification.

  const csrftoken = getCookie('csrftoken'); // Get the token
  let xmlhttp = new XMLHttpRequest();   // Create the request

  xmlhttp.onreadystatechange = function () {
    // Set the success to redirect url
    if (xmlhttp.readyState == XMLHttpRequest.DONE) {
      if (xmlhttp.status == 200) {
        window.location.replace(redirectURL)
      } else {
        // give an error message if the request wasn't successful
        alert(`Error processing your request, please try again`);
      }
    }
  };

  // Create a delete request.
  xmlhttp.open("DELETE", removeNotificationURL, true);
  // pass in the url token to the header
  xmlhttp.setRequestHeader("x-CSRFToken", csrftoken);
  // sends the data
  xmlhttp.send();
}