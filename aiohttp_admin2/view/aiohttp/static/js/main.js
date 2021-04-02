/**
 *  This function provide logic for infinity scroll at list page.
 */
function loadMore(element) {
  if (element.classList.contains('disabled')) {
    return;
  }

  element.classList.add('disabled');

  const nextIdAttr = 'data-next-id';
  const cursorParam = location.href.includes('?') ? '&cursor=' : '?cursor=';
  const lastId = element.getAttribute(nextIdAttr);
  const url = location.href + cursorParam + lastId;


  fetch(url).then(data => {
    data.text().then(text => {
      if (data.status === 200) {

        // add received html to out list of items
        document.querySelector('#table-list').innerHTML += text;

        const newLastId = document
          .querySelector('#scroll_id')
          .getAttribute(nextIdAttr);

        if (newLastId) {
          // set to our button a new next-id attr
          element.setAttribute(nextIdAttr, newLastId);
          // remove unnecessary element
          document.querySelector('#scroll_id').remove();

          if (newLastId === 'None') {
            element.classList.add('disabled');
          } else {
            element.classList.remove('disabled');
          }
        }
      } else {
        console.error(text);
      }
    })
  });
}
