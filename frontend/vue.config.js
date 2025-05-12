const webpack = require('webpack')

module.exports = {
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
      })
    ]
  },
  devServer: {
    // (optional) if you see WS disconnects, match your host/port here
    host: '0.0.0.0',
    client: {
      webSocketURL: 'ws://localhost:8080/ws'
    }
  }
}
