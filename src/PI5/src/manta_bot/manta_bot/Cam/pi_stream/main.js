const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROS = '/opt/ros/jazzy/setup.bash';

// Loop omhoog vanaf deze map tot we install/setup.bash vinden (of gebruik $WS_SETUP)
function findWorkspaceSetup() {
  if (process.env.WS_SETUP) return process.env.WS_SETUP;
  let dir = __dirname;
  while (true) {
    const candidate = path.join(dir, 'install', 'setup.bash');
    if (fs.existsSync(candidate)) return candidate;
    const parent = path.dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}

const WS = findWorkspaceSetup();
if (!WS) {
  console.error('install/setup.bash niet gevonden. Bouw eerst met colcon build, ' +
                'of zet WS_SETUP=/pad/naar/install/setup.bash');
  process.exit(1);
}
console.log(`Workspace: ${WS}`);

const children = [];
const run = (cmd) => {
  const p = spawn('bash', ['-c', `source ${ROS} && source ${WS} && exec ${cmd}`], {
    stdio: 'inherit',
  });
  children.push(p);
  return p;
};

const shutdown = () => {
  children.forEach((c) => c.kill('SIGINT'));
  setTimeout(() => process.exit(0), 1000);
};
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

run('ros2 run manta_bot camera_publisher');
setTimeout(() => run(
  'ros2 run manta_bot yolo_detector --ros-args -p model_name:=yolo26n_ncnn_model'
), 1000);
setTimeout(() => run('ros2 run pi_stream stream'), 2000); 
// evt als nodig veranderen naar setTimeout(() => run('ros2 run manta_bot stream'), 2000);

setTimeout(() => children.push(spawn('ngrok', ['http', '9090'], { stdio: 'inherit' })), 4000);
