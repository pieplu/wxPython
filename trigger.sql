CREATE OR REPLACE TRIGGER MAJSyl
BEFORE INSERT ON sylabes
BEGIN
    IF :NEW
	UPDATE GroupeCours
	SET nbInscriptions = nbInscriptions + 1
	WHERE sigle = :NEW.sigle AND noGroupe = :NEW.noGroupe AND codeSession = :NEW.codeSession;
END;
/