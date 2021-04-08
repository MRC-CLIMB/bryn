const pages = {
  base: {
    entry: "src/base.js",
    template: "public/base.html",
    filename: "../../templates/base.html", // Used as base Django base template for non-Vue views
    title: "CLIMB | Cloud Infrastructure for Microbial Informatics",
    chunks: ["chunk-vendors", "chunk-common", "base"],
  },
  index: {
    entry: "src/main.js",
    template: "public/index.html",
    filename: "../../templates/home/index.html", // Used as Django template for the Vue SPA
    title: "CLIMB | Dashboard",
    chunks: ["chunk-vendors", "chunk-common", "base", "index"],
  },
};

module.exports = {
  publicPath: "/static/vue/",
  outputDir: "./build/static/vue/",

  pages: pages,

  devServer: {
    proxy: {
      ["^(?!/static/vue/)(?!/sockjs-node/)"]: {
        target: "http://localhost:8000",
      },
    },
    host: "localhost", // Without this, HMR will route to local network e.g. 192.168.1.2:8080/socksjs-node/ and fail
  },

  chainWebpack: (config) => {
    config.module
      .rule("md")
      .test(/\.md$/)
      .use("raw-loader")
      .loader("raw-loader");
  },

  pluginOptions: {
    webpackBundleAnalyzer: {
      openAnalyzer: false,
    },
  },
};
