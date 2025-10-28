let headStabilizer = 0.7; 
let smooth = 0.15;

function fixOvershoot(inputX, inputY) {
  let limit = Math.sqrt(inputX * inputX + inputY * inputY);
  if (limit > 1) {
    inputX /= limit;
    inputY /= limit;
  }

  inputX *= headStabilizer;
  inputY *= headStabilizer;


  let fixedX = inputX * (1 - smooth);
  let fixedY = inputY * (1 - smooth);

  return { x: fixedX, y: fixedY };
}

function aimFixLoop() {
  let x = Math.random() * 2 - 1;
  let y = Math.random() * 2 - 1;

  let fixed = fixOvershoot(x, y);
  return fixed;
}

aimFixLoop();
