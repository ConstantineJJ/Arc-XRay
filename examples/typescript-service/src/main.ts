// Synthetic static-analysis fixture. No packages need to be installed.
import {handle} from './handler.js';
import express from 'express';

const app = express();
app.get('/items', handle);
app.listen(3000);
