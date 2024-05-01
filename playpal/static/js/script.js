// A sellector function.

document.addEventListener('DOMContentLoaded', function () {
  //Grabs elements
  const selectElement = selector => {
    const element = document.querySelector(selector)
    if (element) return element;
    throw new Error(`Sorry, that wasn't right, there is no \
    element by the name "{selector}", Please check your spelling and try again!`);
  };

  console.log(selectElement('.hello'));
})
