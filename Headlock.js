let aim = 0;
let focus = 0;
let smooth = 0;

for (let i = 0; i < 10; i++) {
  aim += (Math.random() * 1.4) + 0.6;
  focus += (Math.random() * 0.9) + 0.5;
  smooth = (aim + focus) / 2;
}

smooth = Math.min(smooth, 1.8);
smooth = Math.max(smooth, 1.0);

let lock = (smooth * 1.15).toFixed(2);
