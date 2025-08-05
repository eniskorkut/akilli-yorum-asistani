const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const PORT = 8080;

app.use(cors());
app.use(express.json());

// Yorumları çekme endpoint'i
app.post('/fetch-reviews', (req, res) => {
  const { product_url } = req.body;
  if (!product_url) {
    return res.status(400).json({ error: 'product_url zorunludur.' });
  }

  console.log(`Yorumlar çekiliyor: ${product_url}`);

  // Python scriptini çalıştır
  const py = spawn('python', [
    '1_fetch_reviews.py',
    '--url', product_url,
    '--max-pages', '5',
    '--max-reviews', '50'
  ], {
    cwd: path.join(__dirname, 'ai_core')
  });

  let output = '';
  let errorOutput = '';

  py.stdout.on('data', (data) => {
    output += data.toString();
    console.log('Python output:', data.toString());
  });

  py.stderr.on('data', (data) => {
    errorOutput += data.toString();
    console.error('Python error:', data.toString());
  });

  py.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ 
        error: 'Yorumlar çekilemedi', 
        details: errorOutput,
        output: output 
      });
    }
    
    // Yorumlar çekildikten sonra RAG index'ini güncelle
    updateRagIndex(res, output);
  });
});

// RAG index'ini güncelle
function updateRagIndex(res, fetchOutput) {
  console.log('RAG index güncelleniyor...');
  
  const py = spawn('python', ['2_create_rag_index.py'], {
    cwd: path.join(__dirname, 'ai_core')
  });

  let output = '';
  let errorOutput = '';

  py.stdout.on('data', (data) => {
    output += data.toString();
    console.log('RAG output:', data.toString());
  });

  py.stderr.on('data', (data) => {
    errorOutput += data.toString();
    console.error('RAG error:', data.toString());
  });

  py.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ 
        error: 'RAG index güncellenemedi', 
        details: errorOutput,
        fetchOutput: fetchOutput 
      });
    }
    
    res.json({ 
      success: true, 
      message: 'Yorumlar çekildi ve RAG index güncellendi',
      fetchOutput: fetchOutput,
      ragOutput: output 
    });
  });
}

// Analiz endpoint'i (mevcut yorumlardan soru yanıtlar)
app.post('/analyze', (req, res) => {
  const { question } = req.body;
  if (!question) {
    return res.status(400).json({ error: 'question zorunludur.' });
  }

  console.log(`Soru analiz ediliyor: ${question}`);

  // Python scriptini çalıştır (Gerçek Gemini API)
  const py = spawn('python', [
    '3_query_rag.py',
    '--question', question
  ], {
    cwd: path.join(__dirname, 'ai_core')
  });

  let output = '';
  let errorOutput = '';

  py.stdout.on('data', (data) => {
    output += data.toString();
  });

  py.stderr.on('data', (data) => {
    errorOutput += data.toString();
  });

  py.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: 'Python script hatası', details: errorOutput });
    }
    res.json({ answer: output.trim() });
  });
});

// Yorumları çek ve analiz et (tek seferde)
app.post('/fetch-and-analyze', async (req, res) => {
  const { question, product_url } = req.body;
  if (!question || !product_url) {
    return res.status(400).json({ error: 'question ve product_url zorunludur.' });
  }

  console.log(`Yorumlar çekiliyor ve analiz ediliyor: ${product_url}`);

  // Önce yorumları çek
  const fetchPy = spawn('python', [
    '1_fetch_reviews.py',
    '--url', product_url,
    '--max-pages', '2',
    '--max-reviews', '100'
  ], {
    cwd: path.join(__dirname, 'ai_core'),
    timeout: 300000 // 5 dakika timeout
  });

  let fetchOutput = '';
  let fetchError = '';

  fetchPy.stdout.on('data', (data) => {
    fetchOutput += data.toString();
  });

  fetchPy.stderr.on('data', (data) => {
    fetchError += data.toString();
  });

  fetchPy.on('close', (fetchCode) => {
    if (fetchCode !== 0) {
      return res.status(500).json({ 
        error: 'Yorumlar çekilemedi', 
        details: fetchError 
      });
    }

    // RAG index'ini güncelle
    const ragPy = spawn('python', ['2_create_rag_index.py'], {
      cwd: path.join(__dirname, 'ai_core'),
      timeout: 120000 // 2 dakika timeout
    });

    let ragOutput = '';
    let ragError = '';

    ragPy.stdout.on('data', (data) => {
      ragOutput += data.toString();
    });

    ragPy.stderr.on('data', (data) => {
      ragError += data.toString();
    });

    ragPy.on('close', (ragCode) => {
      if (ragCode !== 0) {
        return res.status(500).json({ 
          error: 'RAG index güncellenemedi', 
          details: ragError 
        });
      }

      // Son olarak soruyu analiz et
      const queryPy = spawn('python', [
        '3_query_rag.py',
        '--question', question
      ], {
        cwd: path.join(__dirname, 'ai_core'),
        timeout: 120000 // 2 dakika timeout
      });

      let queryOutput = '';
      let queryError = '';

      queryPy.stdout.on('data', (data) => {
        queryOutput += data.toString();
      });

      queryPy.stderr.on('data', (data) => {
        queryError += data.toString();
      });

      queryPy.on('close', (queryCode) => {
        if (queryCode !== 0) {
          return res.status(500).json({ 
            error: 'Soru analiz edilemedi', 
            details: queryError 
          });
        }

        res.json({ 
          answer: queryOutput.trim(),
          fetchOutput: fetchOutput,
          ragOutput: ragOutput
        });
      });
    });
  });

  fetchPy.on('error', (error) => {
    if (error.code === 'ETIMEDOUT') {
      return res.status(408).json({ 
        error: 'Yorum çekme işlemi zaman aşımına uğradı', 
        details: 'İşlem 2 dakikadan uzun sürdü'
      });
    }
    return res.status(500).json({ 
      error: 'Yorum çekme hatası', 
      details: error.message 
    });
  });
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
