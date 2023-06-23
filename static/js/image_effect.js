var objectBooksImage = document.getElementsByClassName("postsImg"); // ищем элементы по классу
var opacityBookImage_1 = 1; // прозрачность картинки
var onChangeBooksImageOpacityEnter_1; // функция плавного начала смены прозрачности
var onChangeBooksImageOpacityExit_1; // функция плавного конца смены прозрачности

function OnChangeBooksImageEnter_1() { // функция наведения на картинку
    clearTimeout(onChangeBooksImageOpacityExit_1); // останавливаем функцию плавного конца смены прозрачности
    onChangeBooksImageOpacityEnter_1 = setTimeout(OnChangeBooksImageOpacityEnter_1, 10); // запускаем функцию начала смены прозрачности
}
function OnChangeBooksImageOpacityEnter_1() { // функция начала смены прозрачности
    if(opacityBookImage_1 > 0.8) { // если прозрачность больше 0.1
        opacityBookImage_1 -= 0.01; // уменьшаем прозрачность
        objectBooksImage[0].style.opacity = opacityBookImage_1; // меняяем прозрачность элемента
        onChangeBooksImageOpacityEnter_1 = setTimeout(OnChangeBooksImageOpacityEnter_1, 10); // запускаем смены прозрачности
    }
}
function OnChangeBooksImageOpacityExit_1() { // функция конца смены прозрачности
    if(opacityBookImage_1 < 1) { // если прозрачность меньше 1
        opacityBookImage_1 += 0.01; // увеличиваем прозрачность
        objectBooksImage[0].style.opacity = opacityBookImage_1; // изменяем прозрачность элемента
        onChangeBooksImageOpacityExit_1 = setTimeout(OnChangeBooksImageOpacityExit_1, 50); // запускаем смены прозрачности
    }
}
function OnChangeBooksExit_1() { // функция сведения курсора с картинки
    clearTimeout(onChangeBooksImageOpacityEnter_1); // останавливаем функцию плавного начала смены прозрачности
    onChangeBooksImageOpacityExit_1 = setTimeout(OnChangeBooksImageOpacityExit_1, 50); // запускаем функция конца смены прозрачности
}