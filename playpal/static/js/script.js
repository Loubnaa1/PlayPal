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

function shareToggle(parent_id) {
  const container = document.getElementById(parent_id);
  if (container.classList.contains('d-none')) {
    container.classList.remove('d-none');
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

function formatTags() {
  const elements = document.getElementsByClassName('body');
  for (let i = 0; i < elements.length; i++) {
    let bodyText = elements[i].children[0].innerText;

    let words = bodyText.split(' ');

    for (let j = 0; j < words.length; j++) {
      if (words[j][0] === '#') {
        let url = '/core/explore?query=' + encodeURIComponent(words[j].substring(0));
        let replaceText = bodyText.replace(/\s\#(.*?)(\s|$)/g, `<a href="${url}">${words[j]}</a>`);
        elements[i].innerHTML = replaceText;
      }
    }
  }
}


formatTags();
