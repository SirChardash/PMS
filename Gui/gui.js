const fullLength = 400;
const opacityPadding = 0.2;
const opacityRange = 0.6;

function checkCategory(url, svg, text) {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');


    xhr.onreadystatechange = function () {
        if (this.readyState !== 4) return;

        if (this.status === 200) {
            Object.entries(JSON.parse(this.responseText)).map(([category, probability]) => {
                let graphBar = svg.getElementById(category + '-rect');
                graphBar.setAttributeNS(null, 'width',
                    fullLength * probability + "px");
                graphBar.setAttributeNS(null, 'fill-opacity',
                    opacityPadding + opacityRange * probability + "");
            });
        } else {
            alert("Servis nije dostupan. Provjerite url do servisa.");
        }
    };

    xhr.send(JSON.stringify({
        text: text
    }));
}

function clearEditor(editor) {
    editor.value = '';
}

function readSingleFile(e) {
    const file = e.target.files[0];
    if (!file) {
        return;
    }
    const reader = new FileReader();
    reader.onload = function (e) {
        document.getElementById('text-area').value = e.target.result;
        updateTextInfo(document.getElementById('text-area'));
    };
    reader.readAsText(file);
}

function updateTextInfo(text) {
    document.getElementById('log-values').innerHTML = countWords(text.value) + "<br>" + text.value.length;
}

function countWords(s) {
    s = s.replace(/(^\s*)|(\s*$)/gi, "");
    s = s.replace(/[ ]{2,}/gi, " ");
    s = s.replace(/\n /, "\n");
    return s.split(' ').filter(function (str) {
        return str !== "";
    }).length;
}

function changeFont(editor) {
    if (editor.classList.contains('times-new-roman-font')) {
        editor.classList.remove('times-new-roman-font');
    } else {
        editor.classList.add('times-new-roman-font');
    }
}

function playJazz(element) {
    element.innerHTML = '<iframe width="100%" ' +
        'height="100%" ' +
        'src="https://www.youtube.com/embed/Hrr3dp7zRQY?&autoplay=1" ' +
        'allow="autoplay"></iframe>'
}