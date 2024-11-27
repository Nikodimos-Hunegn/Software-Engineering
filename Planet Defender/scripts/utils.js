function getCenter(e) {
	const {left, top, width, height} = e.getBoundingClientRect();
    return {x: left + width / 2, y: top + height / 2}
}

// Obstacle movement controls

function moveObstacle(){
	const obstacles = document.querySelectorAll('.obstacle')
	let last = obstacles[obstacles.length - 1]
	let position = last.getBoundingClientRect()

	last.style.transform = `translate(${660 - position.x}px,${323 - position.y}px)`

	decideSpeed(last.classList[1],last)
}

function decideSpeed(size,obj){
	if(size == 'big'){
		obj.style.transition = 'transform 25s'
	}
	else if(size == 'medium'){
		obj.style.transition = 'transform 30s'

	}
	else{
		obj.style.transition = 'transform 45s'
	}
}