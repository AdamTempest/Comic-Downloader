let chapters   = {};
let comic_name = "";

// let chapters  = {
//   1:["https://upload.wikimedia.org/wikipedia/commons/1/15/Cat_August_2010-4.jpg"],
//   2:['https://media.cnn.com/api/v1/images/stellar/prod/230426141158-sand-cat-9.jpg?c=original&q=w_1280,c_fill'],
//   3:['https://www.humanesociety.org/sites/default/files/2022-08/hl-yp-cats-579652.jpg']
// };

let chap_nums  			= Object.keys(chapters);
let last_read_chapter 	= localStorage.getItem(comic_name);
let current_chapter 	= parseInt(chap_nums[0]);
let box 				= document.getElementById('chapters');

box.addEventListener('change',change_chapters)

if (last_read_chapter){
	current_chapter = parseInt(last_read_chapter);
}

function sleep(ms) {
	return new Promise(resolve => setTimeout(resolve, ms));
}

function loadsImages(chapter_num){
	let title = document.getElementsByTagName('title')[0];
	if(title){
    title.innerHTML = "Chapter " + chapter_num + " of " + comic_name;
  }
  	console.log(chapter_num);
  	console.log(chapters[chapter_num]);
	let root   = document.getElementById('content');
	let images = chapters[chapter_num];
	let imgEle;

	// clears the previous images
	root.innerHTML = "";

	// loads the images
	for (var i=0;i<images.length;i++){
		imgEle  = document.createElement('img');
		imgEle.setAttribute('src',images[i]);
		imgEle.setAttribute("style",'max-width: 100%;height: auto;');
		root.appendChild(imgEle);
	}
}

function next(){
	let last_key = parseInt(chap_nums[chap_nums.length-1]);
	
	if (current_chapter < last_key){
		current_chapter += 1;
	}
	
	loadsImages(current_chapter);
	
	// record the chapter number
	localStorage.setItem(comic_name, current_chapter);
	
	// scrolls to top
	window.scrollTo(0,0);
}

function previous(){
	let first_key = parseInt(chap_nums[0]);
	
	if (current_chapter > first_key){
		current_chapter -= 1;	
	}
	
	loadsImages(current_chapter);
	
	// record the chapter number
	localStorage.setItem(comic_name, current_chapter);

	// scrolls to top
	window.scrollTo(0,0);
}

/*Dropdown Menu*/

function change_chapters(){
	current_chapter = parseInt(box.options[box.selectedIndex].value);
	loadsImages(current_chapter);
}

loadsImages(current_chapter);