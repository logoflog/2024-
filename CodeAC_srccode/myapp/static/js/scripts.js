//get the DOM elements for the image carousel
const wrapper = document.querySelector(".wrapper");
const container = document.querySelector(".html-container");
const carousel = document.querySelector(".carousel");
const htmls = document.querySelectorAll(".iframe");
const buttons = document.querySelectorAll(".button");

const readme = document.querySelector(".readme");
const rd_container = document.querySelector(".readme-container");
const rd_carousel = document.querySelector(".readme-carousel");
const rd_text = document.querySelectorAll(".text-box");

let htmlIndex = 0,
    textIndex = 0;

const slideHtml = () => {
    //Calculate the updates html index
    //console.log("htmls："+htmls.length);
    htmlIndex = (htmlIndex === 6 ? 0 : (htmlIndex === -1 ? 5 : htmlIndex));
    //Updaate the carousel display to show the specified html
    carousel.style.transform = `translate(-${htmlIndex * 1150}px)`
}

const slideText = () => {
    //Calculate the updates html index
    textIndex = (textIndex === 6 ? 0 : (textIndex === -1 ? 5 : textIndex));
    //Updaate the carousel display to show the specified html
    rd_carousel.style.transform = `translateY(-${htmlIndex * 710}px)`
}

//A function that updates the carousel display to show the next or previous image
const updateClick = (e) => {
    //Calculate the uodated html index based on the button clicked
    htmlIndex += e.target.id === "next" ? 1 : -1;
    textIndex += e.target.id === "next" ? 1 : -1;
    //console.log("after："+htmlIndex);
    slideHtml(htmlIndex);
    slideText(textIndex);
}

//Add event listeners to the navigation buttons
buttons.forEach(button => button.addEventListener("click", updateClick));



