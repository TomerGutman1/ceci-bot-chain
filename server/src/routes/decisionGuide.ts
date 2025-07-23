import { Router } from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs/promises';
import { v4 as uuidv4 } from 'uuid';
import { processDecisionGuideRequest } from '../services/decisionGuideService';

const router = Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: async (_req, _file, cb) => {
    const uploadDir = path.join(process.cwd(), 'uploads', 'decision-guide');
    await fs.mkdir(uploadDir, { recursive: true });
    cb(null, uploadDir);
  },
  filename: (_req, file, cb) => {
    const uniqueName = `${uuidv4()}-${file.originalname}`;
    cb(null, uniqueName);
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 8 * 1024 * 1024, // 8MB limit
  },
  fileFilter: (_req, file, cb) => {
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ];
    
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only PDF, DOCX, and TXT files are allowed.'));
    }
  }
});

// Main analysis endpoint
router.post('/analyze', upload.single('file'), async (req: any, res: any) => {
  try {
    let documentText = '';
    let documentInfo = {
      type: 'text' as 'text' | 'file',
      originalName: '',
      size: 0
    };

    // Handle file upload
    if (req.file) {
      documentInfo.type = 'file';
      documentInfo.originalName = req.file.originalname;
      documentInfo.size = req.file.size;
      
      // Extract text based on file type
      const filePath = req.file.path;
      const fileExt = path.extname(req.file.originalname).toLowerCase();
      
      if (fileExt === '.pdf') {
        const pdfParse = require('pdf-parse');
        const dataBuffer = await fs.readFile(filePath);
        const pdfData = await pdfParse(dataBuffer);
        documentText = pdfData.text;
      } else if (fileExt === '.docx') {
        const mammoth = require('mammoth');
        const result = await mammoth.extractRawText({ path: filePath });
        documentText = result.value;
      } else if (fileExt === '.txt') {
        documentText = await fs.readFile(filePath, 'utf-8');
      }
      
      // Clean up uploaded file
      await fs.unlink(filePath);
    } 
    // Handle pasted text
    else if (req.body.text) {
      documentText = req.body.text;
      documentInfo.size = Buffer.byteLength(documentText, 'utf8');
      // Also accept documentInfo from request body
      if (req.body.documentInfo) {
        documentInfo = { ...documentInfo, ...req.body.documentInfo };
      }
    } else {
      return res.status(400).json({ error: 'No file or text provided' });
    }

    // Validate text length
    if (!documentText || documentText.trim().length < 100) {
      return res.status(400).json({ 
        error: 'Document text is too short. Please provide a complete government decision draft.' 
      });
    }

    // Process the decision guide request
    const analysisId = uuidv4();
    const result = await processDecisionGuideRequest({
      id: analysisId,
      text: documentText,
      documentInfo,
      timestamp: new Date()
    });

    res.json({
      id: analysisId,
      ...result
    });

  } catch (error) {
    console.error('[DecisionGuide] Analysis error:', error);
    res.status(500).json({ 
      error: 'Failed to analyze decision draft',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Export results endpoint
router.get('/export/:id', async (req: any, res: any) => {
  try {
    const { id } = req.params;
    const { format } = req.query;
    
    // TODO: Implement export functionality
    // For now, return a placeholder response
    res.json({
      message: 'Export functionality coming soon',
      id,
      format
    });
  } catch (error) {
    console.error('[DecisionGuide] Export error:', error);
    res.status(500).json({ error: 'Failed to export results' });
  }
});

export default router;