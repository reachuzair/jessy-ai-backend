import cors from "cors";

const allowedOrigins = process.env['ALLOWED_ORIGINS']?.split(",") || [
  "http://localhost:5173",
  "http://localhost:3000",
  "https://slickmagic.ai",
  "http://192.168.1.4:3000",
  "https://slick-admin-5njvmgfu2-zain-alis-projects-8294451a.vercel.app",
  "https://slick-admin-fe-seven.vercel.app"
];

export const corsOptions: cors.CorsOptions = {
  origin: function (origin, callback) {
    if (!origin) return callback(null, true);
    if (allowedOrigins.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      callback(new Error("Not allowed by CORS"));
    }
  },
  credentials: true,
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
  allowedHeaders: [
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "Accept",
    "Origin",
  ],
};

export default cors(corsOptions);
