module.exports = {
    future: {
        // removeDeprecatedGapUtilities: true,
        // purgeLayersByDefault: true,
    },
    purge:  {
      enabled: true,
      content: ['./src/**/*.html']
    },
    theme: {
        extend: {
            fontFamily: {
                jetbrainsMono: 'JetBrains Mono'
            }
        },
    },
    variants: {},
    plugins: [],
}
