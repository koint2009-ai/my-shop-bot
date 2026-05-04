const products = [
  { id: 1, name: "Hoodie", price: 50 },
  { id: 2, name: "T-Shirt", price: 25 }
];

let cart = {};

const container = document.getElementById("products");

products.forEach(p => {
  cart[p.id] = 0;

  const div = document.createElement("div");
  div.innerHTML = `
    <h3>${p.name}</h3>
    <p>${p.price}€</p>

    <button onclick="change(${p.id}, -1)">-</button>
    <span id="q-${p.id}">0</span>
    <button onclick="change(${p.id}, 1)">+</button>
  `;

  container.appendChild(div);
});

function change(id, val) {
  cart[id] = Math.max(0, cart[id] + val);
  document.getElementById(`q-${id}`).innerText = cart[id];
}

function checkout() {
  const result = Object.entries(cart)
    .filter(([id, qty]) => qty > 0)
    .map(([id, qty]) => {
      const product = products.find(p => p.id == id);
      return `${product.name} x${qty}`;
    })
    .join("\n");

  if (!result) {
    alert("Корзина пустая");
    return;
  }

  Telegram.WebApp.sendData(result);
}