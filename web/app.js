const tg = window.Telegram.WebApp;

let cart = [];

async function loadProducts(){

    const res = await fetch(
    "https://web-production-3512d.up.railway.app/products"
);

    const products = await res.json();

    const container = document.getElementById("products");

    container.innerHTML = "";

    products.forEach(product => {

        const div = document.createElement("div");

        div.className = "product";

        div.innerHTML = `
            <img src="${product.photo}">

            <div class="info">

                <h2>${product.name}</h2>

                <div class="price">
                    ${product.price}€
                </div>

                <div class="controls">

                    <button onclick="minus('${product.name}')">
                        -
                    </button>

                    <span id="count-${product.name}">
                        0
                    </span>

                    <button onclick="plus('${product.name}', ${product.price})">
                        +
                    </button>

                </div>

            </div>
        `;

        container.appendChild(div);

    });

}

function plus(name, price){

    const item = cart.find(i => i.name === name);

    if(item){

        item.count += 1;

    }else{

        cart.push({
            name,
            price,
            count:1
        });

    }

    update(name);

}

function minus(name){

    const item = cart.find(i => i.name === name);

    if(!item) return;

    item.count -= 1;

    if(item.count <= 0){

        cart = cart.filter(i => i.name !== name);

    }

    update(name);

}

function update(name){

    const item = cart.find(i => i.name === name);

    document.getElementById(
        `count-${name}`
    ).innerText = item ? item.count : 0;

}

function openCart(){

    const modal = document.getElementById("cartModal");

    const items = document.getElementById("cartItems");

    modal.classList.remove("hidden");

    items.innerHTML = "";

    let total = 0;

    cart.forEach(item => {

        total += item.price * item.count;

        items.innerHTML += `
            <p>
                ${item.name} x${item.count}
                =
                ${item.price * item.count}€
            </p>
        `;

    });

    items.innerHTML += `
        <hr>
        <h3>Итого: ${total}€</h3>
    `;

}

function checkout(){

    if(cart.length === 0){

        tg.showPopup({
            message:"Корзина пустая"
        });

        return;

    }

    let text = "🛒 Новый заказ\n\n";

    let total = 0;

    cart.forEach(item => {

        text += `${item.name} x${item.count} = ${item.price * item.count}€\n`;

        total += item.price * item.count;

    });

    text += `\n💰 Итого: ${total}€`;

    tg.sendData(text);

}

loadProducts();
