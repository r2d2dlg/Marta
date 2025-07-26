// Google AI Service - Complete Integration of Google AI Ecosystem
import { LanguageServiceClient } from '@google-cloud/language';
import { TranslationServiceClient } from '@google-cloud/translate';
import { SpeechClient } from '@google-cloud/speech';
import { TextToSpeechClient } from '@google-cloud/text-to-speech';
import { ImageAnnotatorClient } from '@google-cloud/vision';
import { DocumentProcessorServiceClient } from '@google-cloud/documentai';
import { VideoIntelligenceServiceClient } from '@google-cloud/video-intelligence';
import { PredictionServiceClient } from '@google-cloud/aiplatform';

export interface GoogleAIConfig {
  projectId: string;
  location: string;
  keyFilename?: string;
}

export interface AnalysisResult {
  sentiment: {
    score: number;
    magnitude: number;
    label: 'positive' | 'negative' | 'neutral';
  };
  entities: Array<{
    name: string;
    type: string;
    salience: number;
    metadata?: Record<string, string>;
  }>;
  categories: Array<{
    name: string;
    confidence: number;
  }>;
  language: string;
  translation?: {
    text: string;
    detectedLanguage: string;
  };
}

export interface MediaAnalysisResult {
  text?: string;
  objects?: Array<{
    name: string;
    confidence: number;
    boundingBox?: any;
  }>;
  faces?: Array<{
    confidence: number;
    emotions: Record<string, number>;
  }>;
  landmarks?: Array<{
    description: string;
    confidence: number;
    locations: any[];
  }>;
  safeSearchAnnotation?: {
    adult: string;
    spoof: string;
    medical: string;
    violence: string;
    racy: string;
  };
}

export class GoogleAIService {
  private languageClient: LanguageServiceClient;
  private translateClient: TranslationServiceClient;
  private speechClient: SpeechClient;
  private ttsClient: TextToSpeechClient;
  private visionClient: ImageAnnotatorClient;
  private documentClient: DocumentProcessorServiceClient;
  private videoClient: VideoIntelligenceServiceClient;
  private vertexClient: PredictionServiceClient;
  private config: GoogleAIConfig;

  constructor(config: GoogleAIConfig) {
    this.config = config;
    
    const clientConfig = {
      projectId: config.projectId,
      keyFilename: config.keyFilename,
    };

    this.languageClient = new LanguageServiceClient(clientConfig);
    this.translateClient = new TranslationServiceClient(clientConfig);
    this.speechClient = new SpeechClient(clientConfig);
    this.ttsClient = new TextToSpeechClient(clientConfig);
    this.visionClient = new ImageAnnotatorClient(clientConfig);
    this.documentClient = new DocumentProcessorServiceClient(clientConfig);
    this.videoClient = new VideoIntelligenceServiceClient(clientConfig);
    this.vertexClient = new PredictionServiceClient(clientConfig);
  }

  // Natural Language Processing
  async analyzeText(text: string): Promise<AnalysisResult> {
    try {
      const document = {
        content: text,
        type: 'PLAIN_TEXT' as const,
      };

      // Parallel execution of different analyses
      const [
        sentimentResult,
        entitiesResult,
        classificationResult,
        languageResult,
      ] = await Promise.all([
        this.languageClient.analyzeSentiment({ document }),
        this.languageClient.analyzeEntities({ document }),
        this.languageClient.classifyText({ document }).catch(() => null),
        this.translateClient.detectLanguage({
          parent: `projects/${this.config.projectId}/locations/${this.config.location}`,
          content: [text],
        }),
      ]);

      const sentiment = sentimentResult[0].documentSentiment;
      const entities = entitiesResult[0].entities || [];
      const categories = classificationResult?.[0]?.categories || [];
      const detectedLanguage = languageResult[0].languages?.[0]?.languageCode || 'unknown';

      // Auto-translate if not Spanish or English
      let translation;
      if (detectedLanguage !== 'es' && detectedLanguage !== 'en') {
        translation = await this.translateText(text, 'es', detectedLanguage);
      }

      return {
        sentiment: {
          score: sentiment?.score || 0,
          magnitude: sentiment?.magnitude || 0,
          label: this.getSentimentLabel(sentiment?.score || 0),
        },
        entities: entities.map(entity => ({
          name: entity.name || '',
          type: entity.type || 'UNKNOWN',
          salience: entity.salience || 0,
          metadata: entity.metadata || {},
        })),
        categories: categories.map(category => ({
          name: category.name || '',
          confidence: category.confidence || 0,
        })),
        language: detectedLanguage,
        translation,
      };
    } catch (error) {
      console.error('Error analyzing text:', error);
      throw error;
    }
  }

  // Translation Services
  async translateText(
    text: string, 
    targetLanguage: string = 'es',
    sourceLanguage?: string
  ): Promise<{ text: string; detectedLanguage: string }> {
    try {
      const request = {
        parent: `projects/${this.config.projectId}/locations/${this.config.location}`,
        contents: [text],
        targetLanguageCode: targetLanguage,
        sourceLanguageCode: sourceLanguage,
      };

      const [response] = await this.translateClient.translateText(request);
      const translation = response.translations?.[0];

      return {
        text: translation?.translatedText || text,
        detectedLanguage: translation?.detectedLanguageCode || sourceLanguage || 'unknown',
      };
    } catch (error) {
      console.error('Error translating text:', error);
      return { text, detectedLanguage: sourceLanguage || 'unknown' };
    }
  }

  // Speech-to-Text
  async transcribeAudio(audioBuffer: Buffer, languageCode: string = 'es-ES'): Promise<string> {
    try {
      const request = {
        audio: {
          content: audioBuffer.toString('base64'),
        },
        config: {
          encoding: 'WEBM_OPUS' as const,
          sampleRateHertz: 48000,
          languageCode,
          alternativeLanguageCodes: ['en-US', 'es-MX', 'es-AR'],
          enableAutomaticPunctuation: true,
          enableWordTimeOffsets: false,
          model: 'latest_long',
        },
      };

      const [response] = await this.speechClient.recognize(request);
      const transcription = response.results
        ?.map(result => result.alternatives?.[0]?.transcript)
        .join('\n') || '';

      return transcription;
    } catch (error) {
      console.error('Error transcribing audio:', error);
      throw error;
    }
  }

  // Text-to-Speech
  async synthesizeSpeech(text: string, languageCode: string = 'es-ES'): Promise<Buffer> {
    try {
      const request = {
        input: { text },
        voice: { 
          languageCode, 
          name: languageCode === 'es-ES' ? 'es-ES-Standard-A' : 'en-US-Standard-F',
          ssmlGender: 'FEMALE' as const,
        },
        audioConfig: { 
          audioEncoding: 'MP3' as const,
          speakingRate: 1.0,
          pitch: 0.0,
        },
      };

      const [response] = await this.ttsClient.synthesizeSpeech(request);
      return Buffer.from(response.audioContent as Uint8Array);
    } catch (error) {
      console.error('Error synthesizing speech:', error);
      throw error;
    }
  }

  // Computer Vision
  async analyzeImage(imageBuffer: Buffer): Promise<MediaAnalysisResult> {
    try {
      const request = {
        image: { content: imageBuffer.toString('base64') },
        features: [
          { type: 'TEXT_DETECTION' },
          { type: 'OBJECT_LOCALIZATION' },
          { type: 'FACE_DETECTION' },
          { type: 'LANDMARK_DETECTION' },
          { type: 'SAFE_SEARCH_DETECTION' },
          { type: 'LABEL_DETECTION' },
        ],
      };

      const [response] = await this.visionClient.annotateImage(request);

      return {
        text: response.fullTextAnnotation?.text || '',
        objects: response.localizedObjectAnnotations?.map(obj => ({
          name: obj.name || '',
          confidence: obj.score || 0,
          boundingBox: obj.boundingPoly,
        })) || [],
        faces: response.faceAnnotations?.map(face => ({
          confidence: face.detectionConfidence || 0,
          emotions: {
            joy: this.getLikelihoodScore(face.joyLikelihood),
            sorrow: this.getLikelihoodScore(face.sorrowLikelihood),
            anger: this.getLikelihoodScore(face.angerLikelihood),
            surprise: this.getLikelihoodScore(face.surpriseLikelihood),
          },
        })) || [],
        landmarks: response.landmarkAnnotations?.map(landmark => ({
          description: landmark.description || '',
          confidence: landmark.score || 0,
          locations: landmark.locations || [],
        })) || [],
        safeSearchAnnotation: {
          adult: response.safeSearchAnnotation?.adult || 'UNKNOWN',
          spoof: response.safeSearchAnnotation?.spoof || 'UNKNOWN',
          medical: response.safeSearchAnnotation?.medical || 'UNKNOWN',
          violence: response.safeSearchAnnotation?.violence || 'UNKNOWN',
          racy: response.safeSearchAnnotation?.racy || 'UNKNOWN',
        },
      };
    } catch (error) {
      console.error('Error analyzing image:', error);
      throw error;
    }
  }

  // Document AI
  async processDocument(documentBuffer: Buffer, processorName: string): Promise<string> {
    try {
      const request = {
        name: processorName,
        rawDocument: {
          content: documentBuffer.toString('base64'),
          mimeType: 'application/pdf',
        },
      };

      const [response] = await this.documentClient.processDocument(request);
      return response.document?.text || '';
    } catch (error) {
      console.error('Error processing document:', error);
      throw error;
    }
  }

  // Video Intelligence
  async analyzeVideo(videoBuffer: Buffer): Promise<any> {
    try {
      // Upload video to Cloud Storage first (simplified for this example)
      const request = {
        inputContent: videoBuffer.toString('base64'),
        features: [
          'LABEL_DETECTION',
          'TEXT_DETECTION',
          'SPEECH_TRANSCRIPTION',
        ],
        videoContext: {
          speechTranscriptionConfig: {
            languageCode: 'es-ES',
            enableAutomaticPunctuation: true,
          },
        },
      };

      const [operation] = await this.videoClient.annotateVideo(request);
      const [response] = await operation.promise();

      return {
        labels: response.annotationResults?.[0]?.segmentLabelAnnotations || [],
        text: response.annotationResults?.[0]?.textAnnotations || [],
        speech: response.annotationResults?.[0]?.speechTranscriptions || [],
      };
    } catch (error) {
      console.error('Error analyzing video:', error);
      throw error;
    }
  }

  // Vertex AI Predictions
  async predictWithVertexAI(prompt: string, model: string = 'text-bison'): Promise<string> {
    try {
      const endpoint = `projects/${this.config.projectId}/locations/${this.config.location}/publishers/google/models/${model}`;
      
      const instanceValue = {
        prompt,
        temperature: 0.3,
        maxOutputTokens: 1000,
        topP: 0.8,
        topK: 40,
      };

      const request = {
        endpoint,
        instances: [{ structValue: this.objectToStruct(instanceValue) }],
      };

      const [response] = await this.vertexClient.predict(request);
      const prediction = response.predictions?.[0];
      
      return prediction?.structValue?.fields?.content?.stringValue || '';
    } catch (error) {
      console.error('Error with Vertex AI prediction:', error);
      throw error;
    }
  }

  // Helper methods
  private getSentimentLabel(score: number): 'positive' | 'negative' | 'neutral' {
    if (score > 0.25) return 'positive';
    if (score < -0.25) return 'negative';
    return 'neutral';
  }

  private getLikelihoodScore(likelihood?: string): number {
    const scores = {
      'VERY_UNLIKELY': 0.1,
      'UNLIKELY': 0.3,
      'POSSIBLE': 0.5,
      'LIKELY': 0.7,
      'VERY_LIKELY': 0.9,
    };
    return scores[likelihood as keyof typeof scores] || 0;
  }

  private objectToStruct(obj: any): any {
    const struct: any = { fields: {} };
    
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'string') {
        struct.fields[key] = { stringValue: value };
      } else if (typeof value === 'number') {
        struct.fields[key] = { numberValue: value };
      } else if (typeof value === 'boolean') {
        struct.fields[key] = { boolValue: value };
      }
    }
    
    return struct;
  }

  // Comprehensive analysis combining multiple AI services
  async comprehensiveAnalysis(
    content: string,
    contentType: 'text' | 'image' | 'audio' | 'document' = 'text',
    buffer?: Buffer
  ): Promise<any> {
    try {
      const results: any = {};

      switch (contentType) {
        case 'text':
          results.textAnalysis = await this.analyzeText(content);
          break;
          
        case 'image':
          if (buffer) {
            results.imageAnalysis = await this.analyzeImage(buffer);
            if (results.imageAnalysis.text) {
              results.textAnalysis = await this.analyzeText(results.imageAnalysis.text);
            }
          }
          break;
          
        case 'audio':
          if (buffer) {
            const transcription = await this.transcribeAudio(buffer);
            results.transcription = transcription;
            if (transcription) {
              results.textAnalysis = await this.analyzeText(transcription);
            }
          }
          break;
          
        case 'document':
          if (buffer) {
            const documentText = await this.processDocument(buffer, process.env.DOCUMENT_AI_PROCESSOR_NAME || '');
            results.documentText = documentText;
            if (documentText) {
              results.textAnalysis = await this.analyzeText(documentText);
            }
          }
          break;
      }

      return {
        contentType,
        timestamp: new Date().toISOString(),
        ...results,
      };
    } catch (error) {
      console.error('Error in comprehensive analysis:', error);
      throw error;
    }
  }
}