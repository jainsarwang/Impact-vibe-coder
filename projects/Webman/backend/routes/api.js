const express = require('express');
const router = express.Router();
const requestUtil = require('../utils/request');

router.post('/send-request', async (req, res) => {
  try {
    const { method, url, headers, body } = req.body;
    const response = await requestUtil.sendRequest(method, url, headers, body);
    res.json(response);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;