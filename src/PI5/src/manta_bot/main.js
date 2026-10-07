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
  children.forEach((c) => c.kill('SIGTERM'));
  // ngrok ignores SIGINT sometimes; force-kill stragglers, then give the OS a moment
  setTimeout(() => {
    children.forEach((c) => c.kill('SIGKILL'));
    process.exit(0);
  }, 1000);
};
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

// Kill any orphaned ngrok from a previous run, otherwise ngrok fails with
// ERR_NGROK_334 ("endpoint is already online")
const { execSync } = require('child_process');
try {
  const pids = execSync("pgrep -f 'ngrok http' || true").toString().trim();
  if (pids) {
    console.log(`Killing stale ngrok process(es): ${pids.split('\n').join(', ')}`);
    execSync(`kill ${pids.split('\n').join(' ')} 2>/dev/null || true`);
    // Wait until the tunnel is actually gone (endpoint release can take a moment)
    for (let i = 0; i < 10; i++) {
      const still = execSync("pgrep -f 'ngrok http' || true").toString().trim();
      if (!still) break;
      execSync('sleep 1');
    }
  }
} catch (e) {
  // pgrep/kill unavailable or nothing to kill — ignore
}

run('ros2 run manta_bot camera_publisher');

setTimeout(() => run(
  'ros2 run manta_bot yolo_detector --ros-args -p model_name:=yolo26n_ncnn_model'
), 1000);

setTimeout(() => run('ros2 run manta_bot stream'), 2000);

// Start ngrok after the stream server has had time to start
setTimeout(() => {
  const ngrok = spawn('ngrok', ['http', '127.0.0.1:9091'], {
    stdio: 'inherit',
  });
  children.push(ngrok);
}, 4000);

