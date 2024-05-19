document.addEventListener('DOMContentLoaded', function() {
  const inventoryList = document.getElementById('inventory-list');
  const addButton = document.getElementById('add-button');
  const newNameInput = document.getElementById('new-name');
  const newQuantityInput = document.getElementById('new-quantity');
  const newSectionSelect = document.getElementById('new-section');

  const sections = ['shelf 1', 'shelf 2', 'shelf 3', 'shelf 4', 'bottom basket', 'door'];

  function fetchInventory() {
      fetch('/get')
          .then(response => response.json())
          .then(data => {
              inventoryList.innerHTML = '';
              sections.forEach(section => {
                  const sectionDiv = document.createElement('div');
                  sectionDiv.classList.add('section');
                  sectionDiv.innerHTML = `<h3>${section}</h3>`;
                  const itemsDiv = document.createElement('div');
                  itemsDiv.classList.add('items');

                  data.filter(item => item[3] === section).forEach(item => {
                      const itemDiv = document.createElement('div');
                      itemDiv.classList.add('inventory-item');
                      itemDiv.innerHTML = `
                          <div>Name: <input type="text" value="${item[2]}" id="name-${item[0]}"></div>
                          <div>Quantity: <input type="number" value="${item[1]}" id="quantity-${item[0]}"></div>
                          <div>Section: <select id="section-${item[0]}">
                              ${sections.map(sec => `<option value="${sec}" ${sec === item[3] ? 'selected' : ''}>${sec}</option>`).join('')}
                          </select></div>
                          <button onclick="updateItem(${item[0]})">Update</button>
                          <button onclick="deleteItem(${item[0]})">Delete</button>
                      `;
                      itemsDiv.appendChild(itemDiv);
                  });

                  sectionDiv.appendChild(itemsDiv);
                  inventoryList.appendChild(sectionDiv);
              });
          });
  }

  function addItem() {
      // Perform client-side validation
      if (!newNameInput.value || !newQuantityInput.value || !newSectionSelect.value) {
          alert('Please fill in all fields.');
          return;
      }

      const item = {
          quantity: parseInt(newQuantityInput.value),
          name: newNameInput.value,
          section: newSectionSelect.value,
      };

      fetch('/add', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(item),
      })
      .then(response => response.json())
      .then(() => {
          fetchInventory();
          newNameInput.value = '';
          newQuantityInput.value = '';
          newSectionSelect.value = '';
      });
  }

  window.updateItem = function(id) {
      const item = {
          name: document.getElementById(`name-${id}`).value,
          quantity: parseInt(document.getElementById(`quantity-${id}`).value),
          section: document.getElementById(`section-${id}`).value,
      };

      fetch(`/update/${id}`, {
          method: 'PUT',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify(item),
      })
      .then(response => response.json())
      .then(() => fetchInventory());
  }

  window.deleteItem = function(id) {
      fetch(`/delete/${id}`, {
          method: 'DELETE',
      })
      .then(response => response.json())
      .then(() => fetchInventory());
  }

  addButton.addEventListener('click', function(event) {
      event.preventDefault();
      addItem();
  });

  fetchInventory();
});
