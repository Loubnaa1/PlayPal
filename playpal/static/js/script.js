// A sellector function.

document.addEventListener('DOMContentLoaded', function () {
  //Grabs elements
  const selectElement = selector => {
    const element = document.querySelector(selector)
    if (element) return element;
    throw new Error(`Sorry, that wasn't right, there is no \
    element by the name "${selector}", Please check your spelling and try again!`);
  };

  // Get the "more" option element and the dropdown menu
  const moreOptionElement = selectElement('#more-options');
  const dropdownMenu = selectElement('#dropdown-menu');
  const moreIcon = moreOptionElement.querySelector('.ri-more-2-line')

  // Toggle the dropdown menu when the "more opiton is clicked upon "
  moreOptionElement.addEventListener('click', () => {
    if (moreOptionElement.classList.contains('show')) {
      moreOptionElement.classList.remove('show');
      dropdownMenu.classList.remove('show');
      moreIcon.classList.remove('hide');
    } else {
      dropdownMenu.classList.toggle('show');
      moreOptionElement.classList.toggle('show');
      moreIcon.classList.toggle('hide')
    }
  });

  // Close the dropdown menu when clicking outside of it
  document.addEventListener('click', (event) => {
    if (!moreOptionElement.contains(event.target)) {
      moreOptionElement.classList.remove('show');
      dropdownMenu.classList.remove('show');
      moreIcon.classList.remove('hide');
    }
  });

  const toggleCommentIcon = selectElement('.ri-chat-3-line');
  const commentComponent = selectElement('#comment');

  // Add click event listener to main-comment
  toggleCommentIcon.addEventListener('click', () => {
    commentComponent.classList.toggle('show');
    toggleCommentIcon.classList.toggle('active');
});

});
