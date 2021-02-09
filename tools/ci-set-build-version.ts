const fs = require("fs");
const path = require("path");
const semanticRelease = require("semantic-release");
const { WritableStreamBuffer } = require("stream-buffers");

const stdoutBuffer = new WritableStreamBuffer();
const stderrBuffer = new WritableStreamBuffer();

function getBuildVersion() {
  return semanticRelease(
    {
      // Core options
      dryRun: true,
      branch: "master",
      repositoryUrl: "https://github.com/justindujardin/pathy.git"
    },
    {
      cwd: "./",
      stdout: stdoutBuffer,
      stderr: stderrBuffer
    }
  ).then((result: any) => {
    if (result) {
      const { nextRelease } = result;
      return nextRelease.version;
    }
    return Promise.reject(null);
  });
}

getBuildVersion()
  .then((version: any) => {
    console.log("--- UPDATING build version in python modules to : " + version);
    const filePath = path.join(__dirname, "../pathy/about.py");
    if (!fs.existsSync(filePath)) {
      console.error("pathy.py is missing!");
      process.exit(1);
    }
    const contents = fs.readFileSync(filePath, "utf8");
    const regexp = new RegExp(
      /(__version__\s?=\s?["\'])\d+\.\d+(?:\.\d+)?(["\'])/
    );
    const match = contents.match(regexp);
    if (!match || match.length !== 3) {
      console.error('__version__="x.x.x" string in pathy.py was not found.');
    }
    const replaceVersion = `${match[1]}${version}${match[2]}`;
    const newContents = contents.replace(regexp, replaceVersion);
    fs.writeFileSync(filePath, newContents, "utf8");
  })
  .catch((e: any) => {
    console.log(e);
    console.log(
      "--- SKIPPING update of build versions because no release is required"
    );
  });
