
// Cursor following shooter

function getCenter(e) {
	const {left, top, width, height} = e.getBoundingClientRect();
    return {x: left + width / 2, y: top + height / 2}
}

const arrow = document.querySelector("#arrow");
const arrowCenter = getCenter(arrow);
addEventListener("mousemove", ({clientX, clientY}) => {
    const angle = Math.atan2(clientY - arrowCenter.y, clientX - arrowCenter.x);
    arrow.style.transform = `rotate(${angle}rad)`;
});

// Revolving earth

let i = 1

setInterval(()=>{
	i++
	document.querySelector('#earth').style.transform = `rotate(${i/2}deg)`
},100)

// Obstacle creation

const meteroid = ['small','big','medium']
const side = ['lr','ud']
const updown = ['up','down']
const leftright = ['left','right']
var obastacleId = 0

function randomGenerator(){

	let index = Math.floor(Math.random()*3)
	let lr = Math.floor(Math.random()*2)
	let lat = Math.floor(Math.random()*100)
	let direction = Math.floor(Math.random()*2)

	return [direction,lat,lr,index]

}

function createMeteroid(){

	obastacleId++

	const obstacle = document.createElement('img')

	obstacle.src = 'assets/images/rock.png'

	obstacle.id = `o${obastacleId}`

	obstacle.classList.add('obstacle')

	let a = randomGenerator()


	if(side[a[0]] == 'lr'){
		obstacle.style.top = `${a[1]}vh`
		
		if(leftright[a[2]] == 'left'){
			obstacle.style.left = `-150px`
		}
		else{
			obstacle.style.right = '-150px'
		}
	}
	else{
		obstacle.style.left = `${a[1]}vw`
		
		if(updown[a[2]] == 'up'){
			obstacle.style.top = `-150px`
		}
		else{
			obstacle.style.bottom = '-150px'
		}
	}


	obstacle.classList.add(`${meteroid[a[3]]}`)

	document.body.appendChild(obstacle)

	moveObstacle()
}

// Obstacle Movement control

function moveObstacle(){
	const obstacles = document.querySelectorAll('.obstacle')
	let last = obstacles[obstacles.length - 1]
	let position = last.getBoundingClientRect()

	last.style.transform = `translate(${660 - position.x}px,${323 - position.y}px)`

	decideSpeed(last.classList[1],last)
}

function decideSpeed(s,o){
	if(s == 'big'){
		o.style.transition = 'transform 25s'
	}
	else if(s == 'medium'){
		o.style.transition = 'transform 30s'

	}
	else{
		o.style.transition = 'transform 45s'
	}
}


// Shooter control

var u = ''
let x = 0
let y = 0
let c = 0
let b = 0
var bulletId = 1

function bulletCreator(){
	bulletId ++
	const bullet = document.createElement('div')
	bullet.classList.add('rock')
	bullet.id = `b${bulletId}`
	document.body.appendChild(bullet)
}

function direction(f,g){
	const bulletCenter = getCenter(u);

	x = f - bulletCenter.x
	y = g - bulletCenter.y
	let tan = y / x;
	
	if( x < 0){
	 	b = x - 500
	}
	else{
	 	b = x + 500
	}
	c = tan * b

	return {c,b}
}

var gameover = true



document.body.addEventListener('click',(e)=>{
	if(gameover){
	bulletCreator()

	const rock = document.querySelectorAll('.rock')

	u = rock[rock.length - 1]

	let dir = direction(e.clientX,e.clientY)

	if(dir.b < 520 && dir.b > -520 ){
		u.style.transition = '15s transform'
	}

	// console.log(dir.b)

	u.style.transform = `translate(${dir.b}px,${dir.c}px)`
	// setTimeout(()=>{
	// 	for (let i = 0; i < rock.length; i++){
	// 		rock[i].remove()
	// 	}
	// },2300)

	console.log()
}
})


// Collision checker

const earthCenter = getCenter(document.getElementById('earth'))
var scoreBoard = 0

function detectCollision(obstacle,obj){
	const meteroids = document.querySelectorAll(`.${obstacle}`)
	const object = document.querySelectorAll(`.${obj}`)
	var obsrad

	for (let i = 0; i < meteroids.length; i++){
		for (let j=0; j < object.length; j++){
			switch (meteroids[i].classList[1]){
				case 'small':
					obsrad = 35
					break
				case 'medium':
					obsrad = 60
					break
				case 'big':
					obsrad = 75
					break
			}
			var met = getCenter(meteroids[i])
			var objcenter = getCenter(object[j])

			var rad = obsrad + 75
			var dx = objcenter.x - met.x
			var dy = objcenter.y - met.y
			var distance = Math.sqrt(dx * dx + dy * dy) + 50

			if (obj == 'earth') {distance = Math.sqrt(dx * dx + dy * dy) +35}
			if (obj == 'rock') {distance = Math.sqrt(dx * dx + dy * dy) + 50}

			if (obj == 'earth' && distance <= rad) {
				gameover = false
				meteroids.forEach(m => m.remove())
				var bull = document.querySelectorAll('.rock')
				bull.forEach(b => b.remove())
				document.querySelector('h1').style.display = 'block'
				clearInterval(action)
				clearInterval(detection)
				var score = document.querySelector('#scoreboard')
				score.style.left = '520px'
				score.style.top = '500px'
				score.style.color = '#66f542'
				score.innerText = `Your Score is: ${scoreBoard}`
			}
			else if(obj == 'rock' && distance <= rad){
				meteroids[i].remove()
				object[j].remove()
				scoreBoard++
				document.querySelector('#scoreboard').innerHTML = scoreBoard
			}
	}}

}

var action = setInterval(createMeteroid,800)
var detection = setInterval(()=>{detectCollision('obstacle','earth');detectCollision('obstacle','rock')},100)

// Object remover

function removeMeteroid(i){

	document.querySelector(`#${i}`).remove()

}

function removeBullet(){
	document
}