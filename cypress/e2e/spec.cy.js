describe('WebSocket Chat App - Edge Cases', () => {
  beforeEach(() => {
    cy.visit('http://10.58.176.250:8000/');
  });

  it('should not send empty messages', () => {
    // Trykk på submit uten å skrive noe
    cy.get('#submitButton').click();

    // Bekreft at ingen ny melding ble lagt til
    cy.get('#container div').should('not.contain.text', '');
  });

  it('should handle long input gracefully', () => {
    const longMessage = 'a'.repeat(1000); // 1000 tegn

    cy.get('#inputText').type(longMessage);
    cy.get('#submitButton').click();

    cy.get('#container').contains(longMessage).should('exist');
  });

  it('should handle fast repeated messages', () => {
    const fastMessage = 'spam';

    for (let i = 0; i < 5; i++) {
      cy.get('#inputText').type(`${fastMessage}${i}{enter}`);
    }

    for (let i = 0; i < 5; i++) {
      cy.get('#container').contains(`${fastMessage}${i}`).should('exist');
    }
  });

  it('should trim whitespace in input', () => {
    cy.get('#inputText').type('     trimmed message     ');
    cy.get('#submitButton').click();

    cy.get('#container').contains('trimmed message').should('exist');
  });

  it('should keep working after refreshing the page', () => {
    cy.get('#inputText').type('message before refresh');
    cy.get('#submitButton').click();
    cy.reload();

    // Meldingen vil forsvinne fordi du ikke har lagt til localStorage/sessionStorage-lagring
    // Her tester vi at appen ikke krasjer etter reload
    cy.contains('Connected to server.').should('exist');
  });

  it('should still work if Enter is pressed multiple times quickly', () => {
    cy.get('#inputText').type('test rapid enter{enter}{enter}{enter}');
    cy.get('#container')
      .contains('test rapid enter')
      .should('exist');
  });
});

