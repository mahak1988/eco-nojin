export default ({ env }) => ({
  graphql: {
    enabled: true,
    config: {
      endpoint: '/graphql',
      shadowCRUD: true,
      playgroundAlways: env.bool('PLAYGROUND_ALWAYS', false),
      depthLimit: 7,
      amountLimit: 100,
      apolloServer: {
        tracing: true,
      },
    },
  },
});