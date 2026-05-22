const counters = {
  requests: 0
};

function increment() {
  counters.requests += 1;
}

function getCount() {
  return counters.requests;
}

module.exports = {
  increment,
  getCount
};
